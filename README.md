# MomentumSourceIteration
Development of an algorithm for the iterative calculation of momentum source terms in a fluid dynamic model

## What do I want to do?
This repo is a small part of my PhD thesis in the field of fluid dynamics and heat transfer. I am going to talk about an algorithm that I have developed for an important task in my PhD project. With a lot surprise, I realized just now that it is indeed a small learning algorithm I have developed! To be frank, when I did this job, I did not really know anything details about machine learning.

So, I am interested in predicting with numeric methods the fluid field in a special application that involves complex geometry conditions, i.e. heating rod bundles through which coolant flows. Furthermore, certain mixing devices - socalled mixing vanes - are implemented to promote mixing, in order to obtain a relatively uniform distribution of the fluid field. The mixing devices disturb and force the flow to change its behavior in a certain way, and thus, have very complicated effects that requires large efforts to model/predict. One solution is to use Computational Fluid Dynamics (CFD) method that requires to discretize the whole computational domain into more than ten million nodes/cells and solve certain equations (yes, I mean the famous Navier-Stokes equations and various models for turbulence that has bothered Albert Einstein). I did this part of work and predicted the flow field with satisfactory accuracy. However, the CFD solution is not always practical, since it takes A LOT computational resources and is consequently expensive!

## Is there any workaround?
Yes! Engineers are excellent at coming up with (simplified) models that are not always precise, but they work and can provide acceptable results! Other than the expensive CFD method, another alternative solution is to avoid huge amount of computational cells, meaning:
- I can discretize the domain into much fewer nodes/cells and thus obtain a much simpler system; 
- Because of the simplification, it is natural that additional models has to be supplied if equivalent accuracy is expected;
- Unfortunately, it turned out to be extremely difficult to come up with such models from the perspective of physics (Newtonian mechanics);
- Solution: still solve those equations to predict the fluid field, but this time I provide certain parameters to the new simple system and "teach" it how to achieve the "correct" results. 

Sounds a bit fancy, isn't it? Here is the basic logic behind:

- Firstly, I already got accurate results from the expensive CFD method, if you remember;
- Secondly, I build the simplfied system that does not require a lot computational power;
- Thirdly, I investigate these valid results and come up with parameters that can represent certain information provided by the accurate results;
- Then, these parameters are provided to the simplified system, and they tell it how to behave.

In other words, the new simplified system learns from the complicated expensive CFD solution. After the new simplified system learns enough, it becomes sufficiently "smart" and can be expanded to wider applications (of course, under proper conditions) and work independently. The original expensive CFD method is not needed anymore.


## How exactly does the simplified system learn?
In this section I'll talk a bit more about the technical details about the method mentioned above. The accurate results are the target we expect to obtain also from the simpified system. We may also call it training output. The key issue is: how to determine the parameters that can convey proper information to the simplified system and teaches it to behave as expected? Here I would like to insert a bit background of physics: these parameters are actually source terms in the momentum equations of the fluid field; if they are correctly provided, we can obtain correct results from the simplified system. As mentioned in the last section, it is extremely difficult to determine the parameters from physics models. So eventually I design an algorithm to iteratively calculate/train them, based on the accurate results as the training output.

As shown in the flow chart below, the iterative training process consists of the following steps:

1) Start with initially guessed parameters;
2) Perform the computation on the simplified system with the parameters;
3) Extract results from the simplified system;
4) Compare the extracted results with the accurate results (training output);
5) A function evaluating the global degree of agreement between the training output and the results obtained with current parameters is calculated;
6) if a global agreement is achieved, the iterative process is terminated; otherwise the parameters are corrected and steps 2)through 6) are repeated.

Probably as you have already noticed, the essential step in the iteration is to correct the parameters, i.e., to train the parameters. I design the training process on the combination of two levels: global and local. We first have a look at the global level, as shown below:

The correction/training of the parameters on the global level is based on the function used to evaluate the global agreement, as mentioned above (step 6)). This function is the sum of squared errors over my whole computational domain, i.e., all the nodes/cells that result from the discretization.

