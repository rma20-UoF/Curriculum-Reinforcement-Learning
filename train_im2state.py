import copy
import math
import os

import numpy as np
import torch
from torch import optim, nn
import matplotlib.pyplot as plt
from tqdm import tqdm

from a2c_ppo_acktr.arguments import get_args
from eval_pose_estimator import eval_pose_estimator
from im2state.model import PoseEstimator

from im2state.utils import normalise_coords, unnormalise_y, custom_loss

args = get_args()

torch.manual_seed(args.seed)
torch.cuda.manual_seed_all(args.seed)

if args.cuda and torch.cuda.is_available() and args.cuda_deterministic:
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def main():
    torch.set_num_threads(1)
    device = torch.device(f"cuda:{args.device_num}" if args.cuda else "cpu")

    images, abs_positions, rel_positions, low, high, _, _ = torch.load(
        os.path.join(args.load_dir, args.env_name + ".pt"))
    print("Loaded")
    print(len(images))
    low = torch.Tensor(low).to(device)
    high = torch.Tensor(high).to(device)

    save_path = os.path.join('trained_models', 'im2state')
    try:
        os.makedirs(save_path)
    except OSError:
        pass

    positions = rel_positions if args.rel else abs_positions

    pretrained_name = 'vgg16_4out.pt' if args.rel else 'vgg16_3out.pt'
    net = PoseEstimator(3, positions.shape[1])
    # net.load_state_dict(torch.load(os.path.join('trained_models/pretrained/', pretrained_name)))
    net = net.to(device)

    optimizer = optim.Adam(net.parameters(), lr=args.lr)
    criterion = custom_loss

    np_random = np.random.RandomState()
    np_random.seed(1053831)
    p = np_random.permutation(len(images))
    positions = positions[p]

    num_test_examples = images.shape[0] // 10
    num_train_examples = images.shape[0] - num_test_examples
    batch_size = 100

    train_indices = p[:num_test_examples]
    test_indices = p[num_test_examples:]
    test_x = np.array((batch_size, 3, 128, 128))
    for i, idx in enumerate(test_indices):
        test_x[i] = np.transpose(images[i], (2, 0, 1))

    test_y = positions[:num_test_examples]
    train_y = positions[num_test_examples:]

    train_loss_x_axis = []
    train_loss = []
    test_loss = []
    min_test_loss = math.inf

    updates_with_no_improvement = 0

    # run the main training loop
    epochs = 0
    while updates_with_no_improvement < 5:
        for batch_idx in tqdm(range(0, num_train_examples, batch_size)):
            indices = train_indices[batch_idx:batch_idx + batch_size]
            train_x = np.array((batch_size, 3, 128, 128))
            for i, idx in enumerate(indices):
                train_x[i] = np.transpose(images[i], (2, 0, 1))

            output = net.predict(torch.Tensor(train_x).to(device))
            pred_y = output if args.rel else unnormalise_y(output, low, high)
            loss = criterion(pred_y,
                             torch.Tensor(train_y[batch_idx:batch_idx + batch_size]).to(device))
            train_loss += [loss.item()]
            train_loss_x_axis += [epochs + (batch_idx + batch_size) / num_train_examples]

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        epochs += 1

        loss = 0
        with torch.no_grad():
            for batch_idx in tqdm(range(0, num_test_examples, batch_size)):
                test_output = net.predict(torch.Tensor(test_x[batch_idx:batch_idx + batch_size]).to(device))
                test_output = test_output if args.rel else unnormalise_y(test_output, low, high)
                loss += criterion(test_output,
                             torch.Tensor(test_y[batch_idx:batch_idx + batch_size]).to(device)).item()

            test_loss += [loss / (num_test_examples // batch_size)]
        if test_loss[-1] < min_test_loss:
            updates_with_no_improvement = 0
            min_test_loss = test_loss[-1]

            save_model = net
            if args.cuda:
                save_model = copy.deepcopy(net).cpu()
            torch.save(save_model, os.path.join(save_path, args.save_as + ".pt"))
            print("Saved")
        else:
            updates_with_no_improvement += 1

        if epochs % args.log_interval == 0 or updates_with_no_improvement == 5:
            fig = plt.figure()
            plt.plot(train_loss_x_axis, train_loss, label="Training Loss")
            plt.plot(range(1, epochs + 1), test_loss,  label="Test Loss")
            plt.legend()
            plt.savefig(f'imgs/{args.save_as}.png')
            plt.close(fig)
            print(f"Training epoch {epochs} - validation loss: {test_loss[-1]}")

    print("Finished training")
    eval_pose_estimator(os.path.join(save_path, args.save_as + ".pt"), device, torch.Tensor(test_x).to(device),
            torch.Tensor(test_y).to(device),
                        low if not args.rel else None, high if not args.rel else None)


if __name__ == "__main__":
    main()
