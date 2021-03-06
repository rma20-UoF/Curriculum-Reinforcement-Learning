from envs.DRRewardEnvs import DRSparseEnv, DRDenseEnv
from envs.ReachOverWallEnv import ROWSparseEnv, ROWDenseEnv
from envs.ShelfStackEnv import SSSparseEnv, SSDenseEnv

shelf = {
    'sparse': SSSparseEnv,
    'dense': SSDenseEnv,
    'task': 'shelf',
    'curriculum': [
        'shelf_nr',
        'shelf_5',
        'shelf_6',
        'shelf_7',
        'shelf_8',
        'shelf_9',
        'shelf_10',
        'shelf_11',
        'shelf_12',
        'shelf_13',
    ]
}

wall = {
    'sparse': ROWSparseEnv,
    'dense': ROWDenseEnv,
    'task': 'reach_over_wall_static',
    'curriculum': [
        'reach_no_wall',
        'row_30',
        'row_31',
        'row_32',
        'row_33',
        'row_34',
        'row_35',
        'row_36',
        'row_37',
        'row_38',
        'row_39',
        'row_40',
        'row_41',
        'row_42',
        'row_43',
        'row_44',
        'row_45',
        'row_46',
    ]
}

rack = {
    'sparse': DRSparseEnv,
    'dense': DRDenseEnv,
    'task': 'dish_rack',
    'curriculum': [
        'dish_rack_nr',
        'dish_rack_7',
        'dish_rack_8',
        'dish_rack_9',
        'dish_rack_10',
        'dish_rack_11',
    ]
}

pipelines = {
    'shelf': shelf,
    'shelf_1': shelf,
    'shelf_2': {
        'sparse': SSSparseEnv,
        'dense': SSDenseEnv,
        'task': 'shelf',
        'curriculum': [
            'shelf_nr',
            'shelf_5',
            'shelf_7',
            'shelf_9',
            'shelf_11',
            'shelf_13',
        ]
    },
    'shelf_4': {
        'sparse': SSSparseEnv,
        'dense': SSDenseEnv,
        'task': 'shelf',
        'curriculum': [
            'shelf_nr',
            'shelf_5',
            'shelf_9',
            'shelf_13',
        ]
    },
    'shelf_8': {
        'sparse': SSSparseEnv,
        'dense': SSDenseEnv,
        'task': 'shelf',
        'curriculum': [
            'shelf_nr',
            'shelf_5',
            'shelf_13',
        ]
    },
    'shelf_16': {
        'sparse': SSSparseEnv,
        'dense': SSDenseEnv,
        'task': 'shelf',
        'curriculum': [
            'shelf_nr',
        ]
    },
    'shelf_res': {
        'sparse': SSSparseEnv,
        'dense': SSDenseEnv,
        'task': 'shelf',
        'curriculum': []
    },
    'wall': wall,
    'wall_1': wall,
    'wall_2': {
        'sparse': ROWSparseEnv,
        'dense': ROWDenseEnv,
        'task': 'reach_over_wall_static',
        'curriculum': [
            'reach_no_wall',
            'row_30',
            'row_32',
            'row_34',
            'row_36',
            'row_38',
            'row_40',
            'row_42',
            'row_44',
            'row_46',
        ]
    },
    'wall_4': {
        'sparse': ROWSparseEnv,
        'dense': ROWDenseEnv,
        'task': 'reach_over_wall_static',
        'curriculum': [
            'reach_no_wall',
            'row_30',
            'row_34',
            'row_38',
            'row_42',
            'row_46',
        ]
    },
    'wall_8': {
        'sparse': ROWSparseEnv,
        'dense': ROWDenseEnv,
        'task': 'reach_over_wall_static',
        'curriculum': [
            'reach_no_wall',
            'row_30',
            'row_38',
            'row_46',
        ]
    },
    'wall_16': {
        'sparse': ROWSparseEnv,
        'dense': ROWDenseEnv,
        'task': 'reach_over_wall_static',
        'curriculum': [
            'reach_no_wall',
        ]
    },
    'rack': rack,
    'rack_1': rack,
    'rack_2': {
        'sparse': DRSparseEnv,
        'dense': DRDenseEnv,
        'task': 'dish_rack',
        'curriculum': [
            'dish_rack_nr',
            'dish_rack_7',
            'dish_rack_9',
            'dish_rack_11',
        ]
    },
    'rack_4': {
        'sparse': DRSparseEnv,
        'dense': DRDenseEnv,
        'task': 'dish_rack',
        'curriculum': [
            'dish_rack_nr',
            'dish_rack_7',
            'dish_rack_11',
        ]
    },
    'rack_8': {
        'sparse': DRSparseEnv,
        'dense': DRDenseEnv,
        'task': 'dish_rack',
        'curriculum': [
            'dish_rack_nr',
        ]
    },
    'rack_res': {
        'sparse': DRSparseEnv,
        'dense': DRDenseEnv,
        'task': 'dish_rack',
        'curriculum': []
    },
    'rack_vis': {
        'sparse': DRSparseEnv,
        'dense': DRDenseEnv,
        'task': 'dish_rack_vis',
        'curriculum': [
            'dish_rack_vis_nr',
            'dish_rack_vis_7',
            'dish_rack_vis_9',
            'dish_rack_vis_11',
        ]
    },
}



