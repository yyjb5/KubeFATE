# HSE: Horizontal Serving Engine

End-to-end streamlining of setting up an ML serving service for any trained model. Currently, it supports converting
horizontally-trained [FATE](https://github.com/FederatedAI/FATE) model and turns it into
a [KFServing](https://github.com/kubeflow/kfserving) service ready for production usage.

See the [tutorial guide](doc/tutorial_serving_HomoLR.ipynb) for an example of end-to-end workflow - creating an
online serving service from a trained logistic regression model. 