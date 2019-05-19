import pymongo


class MongoManager():
    def __init__(self, server='localhost', port='27017'):
        self._client = pymongo.MongoClient(server, int(port))

    def get_database_names(self, ):
        '''Get all databases on MongoDB'''
        dbl = self._client.list_database_names()
        return dbl

    def init_connection_to_runs(self, db_name):
        '''Generic function to access directly to runs collection of selected database'''
        db = self._client[db_name]
        return db['runs']

    def init_connection_to_metrics(self, db_name):
        db = self._client[db_name]
        return db['metrics']

    def get_experiment_names(self, db_name):
        ''''
        Returns a list of experiments of selected data_base

        :param db_name:
        :return:
        '''
        if db_name is None:
            return []
        collection = self.init_connection_to_runs(db_name)
        exp_names = collection.find({}, {'experiment.name': 1}).distinct('experiment.name')
        return exp_names

    def get_rows_from_exp_names(self, db_name, exp_names, columns):
        collection = self.init_connection_to_runs(db_name)

        filter = {'experiment.name': {'$in': exp_names}}
        projection = dict((col, True) for col in columns)

        cursor = collection.find(filter=filter, projection=projection)

        return cursor

    def get_rows_from_ids(self, db_name, selected_ids, columns):
        collection = self.init_connection_to_runs(db_name)

        filter = {'_id': {'$in': selected_ids}, }
        projection = dict((col, True) for col in columns)

        cursor = collection.find(filter=filter, projection=projection)

        return cursor

    def get_configs_from_ids(self, db_name, selected_ids):
        collection = self.init_connection_to_runs(db_name)
        filter = {'_id': {'$in': selected_ids}, }
        projection = dict(config=True)
        cursor = collection.find(filter=filter, projection=projection)

        return cursor

    def get_from_run_infos(self, attr, db_name, selected_ids):
        collection = self.init_connection_to_runs(db_name)
        filter = {"_id": {"$in": selected_ids}}
        projection = {"info.{}".format(attr): 1}
        return collection.find(filter=filter, projection=projection)

    def get_metrics_infos(self, db_name, selected_ids):
        return self.get_from_run_infos('metrics', db_name, selected_ids)

    def get_metric_data(self, metric_name, db_name, selected_ids):
        collection = self.init_connection_to_metrics(db_name)
        filter = {"name": {"$eq": metric_name}, "run_id": {"$in": selected_ids}}
        cursor = collection.find(filter=filter)
        return cursor

    def get_metrics_data(self, metric_names, db_name, selected_ids):
        collection = self.init_connection_to_metrics(db_name)
        filter = {"name": {"$in": metric_names}, "run_id": {"$in": selected_ids}}
        cursor = collection.find(filter=filter)
        return cursor

    def get_traj_steps_from_id(self, db_name, selected_id):
        metric_name = 'eval_sequence_probas'
        collection = self.init_connection_to_metrics(db_name)
        filter = {"name": metric_name, "run_id": selected_id}
        proj = {'steps': 1}
        return collection.find_one(filter=filter, projection=proj)['steps']

    def get_traj_from_id(self, db_name, selected_id, idx):
        metric_names = ['eval_sequence_probas', 'eval_rewards', 'eval_obs']
        collection = self.init_connection_to_metrics(db_name)
        filter = {"name": {'$in': metric_names}, "run_id": selected_id}
        data = list(collection.find(filter=filter, projection={
            'steps': {'$slice': [idx, 1]},
            'values': {'$slice': [idx, 1]},
        }))

        return dict((elt['name'], elt['values']) for elt in data)
