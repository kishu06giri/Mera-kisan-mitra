# Mera-kisan-mitra
<div align="center">

## AI Wheat Diesase Detector [Recognition of Wheat Plant Diseases by Leaf Image Classification]

### <a href="" target="_blank"></a>



 </div>

## Description

Food security for billions of people on earth requires minimizing crop damage by timely detection of diseases.Developing methods
for detection of plant diseases serves the dual purpose of increasing crop yield and reducing pesticide use without knowing
about the proper disease. Along with development of better crop varieties, disease detection is thus paramount goal for achieving
food security. The traditional method of disease detection has been to use manual examination by either farmers or experts, which
can be time consuming and costly, proving infeasible for millions of small and medium sized farms around the world.

This project is an approach to the development of Wheat plant disease recognition model, based on leaf image classification, by the
use of deep convolutional networks. The developed model is able to recognize 15 different types of plant diseases  with the ability to distinguish plant leaves from their surroundings.

## Leaf Image Classification



This process for building a model which can detect the disease assocaited with the leaf image. The key points to be followed are:

1. Data gathering

   The dataset taken was **"Wheat Plant Diseases"**. It can be downloaded through the link "https://www.kaggle.com/datasets/kushagra3204/wheat-plant-diseases". It is an Image dataset containing images of different healthy and unhealthy crop leaves.

2. Model building

   - I have used pytorch for building the model.
   - I have used Mobilenetv2 for image processing.
   - I used google collab to train the model

3. Training

   The model was trained by using variants of above layers mentioned in model building and by varying hyperparameters. The best model was able to achieve 98.42% of test accuracy.

4. Testing

   The model was tested on total 14155 images of 15 classes.<br/>
 












