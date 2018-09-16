class BaseView(object):
    main_model = []
    l_models = []

    @staticmethod
    def load_view():
        raise NotImplementedError
