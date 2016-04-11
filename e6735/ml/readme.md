feature.py -- some analysis method, may combine some of them to train the model
Two training method:
    trainFeaturesLogistic: using Logistic regression, need a classifier to classify the feature according to score
                            gMM classifier is implemented
    trainModelLeastError: minimize the least error equation to get a score-to-feature mapping equation
    remaining worK:
        trainModelLeastError: automatic generate score basing on the trained data set: PCA -> minimize video&audio error -> map score to feature space
                              automatic generate score criteria: PCA -> minimize video&audio error -> generate score criteria
implemented api:
    clusterLinearModel