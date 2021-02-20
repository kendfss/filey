# sl4ng

This package serves as a workflow booster for emailing, iterating, and a veritable smorgasboard of cases scattered in between. 

You want persistant data but Pickle and Dill ask too many damned questions? 
	sl4ng.persistance.save
	sl4ng.persistance.load

You be writing generators so nice that you want to use them twice, thrice, or indefinitely? We gotchu! 
    sl4ng.types.regenerator 

You're on the brink of the creative breakthrough of the ages but you'll end it all in a fit of rage if you accidentally overwite your projects ever again? We gotchu! 
    sl4ng.files.paths.namespacer

You want to look at an object's source code but inspect.getsource makes a mess of rendering things in your REPL, or perhaps you want to jump straight into its package-folder or source-file? 
    sl4ng.debug.getsource 
    sl4ng.debug.pop 

You want to want to see if your iterable is the codomain of a constant function? We gotchu 
    sl4ng.functional.eq 

You really like your dictionary, but it's got some duplicate values? We.. Got.. Chu! 
    sl4ng.iteration.deduplicate

You've read this far and think "Damn, son, this package looks diggity fresh, but some of those functions are deeply nested"? We gotchu 
    Everything is imported to init