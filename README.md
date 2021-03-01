# Momentum Source Iteration
Development of an algorithm for the iterative calculation of momentum source terms in a fluid dynamic model

## What do I want to do?
This repo is a small part of my PhD project in the field of numerical modeling of fluid dynamics and heat transfer. I am going to talk about an algorithm that I have developed with Python for an important task in my PhD work. With a lot surprise, I realized just now that it is indeed a small learning algorithm I have developed! To be frank, when I did this job, I did not really know any details about machine learning.

So, I am interested in predicting with numeric methods the fluid field in a special application that involves complex geometry conditions, i.e. heating rod bundles through which coolant flows. Furthermore, certain mixing devices - so-called mixing vanes - are implemented to promote mixing, in order to obtain a relatively uniform distribution of the fluid field. The mixing devices disturb and force the flow to change its behavior in a particular way, and thus, have very complicated effects that requires large efforts to calculate. One solution is to use Computational Fluid Dynamics (CFD) method that requires to discretize the whole computational domain into more than ten million nodes/cells and solve certain equations (yes, I mean the famous Navier-Stokes equations and various models for turbulence, which has bothered Albert Einstein). I did this part of work and calculated the flow field with satisfactory accuracy. However, the CFD solution is not always practical, since it takes A LOT computational resources and is consequently expensive!

## Is there any workaround?
Yes! Engineers are excellent at coming up with (simplified) models that are not always precise, but they work and can provide acceptable results! Other than the expensive CFD method, another alternative solution is to avoid huge amount of computational cells:

- I can discretize the domain into much fewer nodes/cells and thus obtain a much simpler system; 
- Because of the simplification, it is natural that additional models have to be supplied if equivalent accuracy is expected;
- Unfortunately, it turned out to be extremely difficult to come up with such models from the perspective of physics (Newtonian mechanics);
- Solution: still solve those equations to obtain the fluid field, but this time I provide certain parameters to the new simple system and "teach" it how to achieve the "correct" results. 

Sounds a bit fancy, isn't it? Here is the basic logic behind:

- First of all, I already got accurate results from the expensive CFD method, if you remember;
- Secondly, I build the simplfied system that does not require a lot computational power;
- Thirdly, I come up with parameters that can represent certain information provided by the accurate results;
- Then, these parameters are provided to the simplified system, and they tell it how to behave.

In other words, the new simplified system learns from the accurate results obtained with the complicated CFD solution. After the new simplified system learns enough, it becomes sufficiently "smart" and can be expanded to wider applications (of course, under proper conditions) and work independently. The original expensive CFD method is not needed anymore.


## How exactly does the simplified system learn?
In this section we walk through more technical details about the method mentioned above. The accurate results are the target we also expect to obtain from the simplified system. We may also call it training output. The key issue is: how to determine the parameters that can convey proper information to the simplified system and teaches it to behave as expected? Here I would like to insert a bit background of physics: these parameters are actually source terms in the momentum equations of the fluid field; if they are correctly provided, we can obtain correct results from the simplified system. As mentioned in the last section, it is extremely difficult to determine the parameters from physics models. So eventually I design an algorithm to iteratively calculate/train them, based on the accurate results as the training output.

### Overview of the iterative training process
As shown in the flow chart below, the iterative training process consists of the following steps:

1) Start with initially guessed parameters;
2) Perform the computation on the simplified system with the parameters;
3) Extract results from the simplified system;
4) Compare the extracted results with the accurate results (training output);
5) A function evaluating the global degree of agreement between the training output and the results obtained with current parameters is calculated;
6) If a global agreement is achieved, the iterative process is terminated; otherwise the parameters need to be corrected and steps 2)through 6) are repeated.

<img src="/flow%20chart%20for%20github.png" height="400">


Probably as you have already noticed, the essential step in the iteration is to correct the parameters, i.e., to train the parameters. I design the training process on the combination of two levels: global and local. 

### Training on global level

The flow chart of the global level training process is shown below:

<img src="/global%20level%20github.png" height="400">


The correction of the parameters means to add or subtract a certain increment to/from them. As you will see in a minute, this increment is actually analogous to the learning rate in the machine learning methods. The global level correction is based on the function used to evaluate the global agreement between the simplified system and the accurate results, as mentioned above (step 6)). This function is the sum of squared errors (SSE) over my whole computational domain, i.e., all the nodes/cells that result from the discretization. Basically, in every iteration SSE is calculated and compared to the previous iteration. If SSE has decreased a lot, it means the current parameters have helped a lot approaching the training output and we can even make larger changes to the parameters to make them more effective and obtain faster approach towards the training output. This is completed by increasing the increment by a certain factor (the factor is 2, in my current case).

In contrast, if the SSE is not decreasing or even increasing, it means the simplified system is getting worse results compared to last iteration. This is caused by over-correction of the parameters. In this case we have to prevent the current parameters from developing in their current trend. This is done by decreasing the increment by a certain factor.

The third case is that, SSE is decreasing, but not by a lot. This means the current parameters are working fine: they are driving the simplified system to approach the training output. But we'd better not change the parameters, otherwise they are prone to the risk of over-correction.

After the correction on global level, we enter the step of correction on local level.


### Training on local level

In this specific application scenario, the discretized nodes/cells in the simplified system are linked to a clear spacial representation (please recall that I have been trying to calculate the fluid field in some geometry). Therefore, it is a good idea to do a node-wise examination to see the local agreement between the results obtained on the simplified system and the training output. If for some nodes/cells, large deviation is observed, local corrections to the corresponding parameters should be applied. In other words, in the step of local level correction, the increments that are used to correct the parameters are further trained on a node-wise level. This is why I call it local level training. The benefit is clear: the simplified system approaches the training output faster.

After enough iterations containing both global and local level training, SSE converges to a value that is small enough, as shown in the figure below:

<img src="/SSE.png" height="400">

The corresponding final parameters are the results of the training process. At this point, the simplified system is said to be "smart" enough. It can reproduce the training output very well with the final parameters. It's worth noticing that in this application I do not need to worry about overfitting, because the physical problem I have been solving is fundamentally deterministic and the goal is to reproduce the accurate results to the largest extent. In other words, after the training process that works nicely, we are not concerned with any prediction process that is involved in traditional machine learning activities. The simplified system, the final parameters as well as the whole methodology can be applied in extended applications. 

The corresponding code is in the file "iteration_xflowfactor.py". A separate programm called CTF is used to solve the Navier-Stokes equations for the simplified system. A few functions that process the output files of CTF are also included in the file "iteration_xflowfactor.py".
