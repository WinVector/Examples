package com.mzlabs.fit;

public interface Link {
	/**
	 * 
	 * @param z
	 * @param res res.length==3, set to (f^{-1}(z),d/dz f^{-1}(z), d^2/dz^2 f^{-1}(z)
	 */
	void invLink(double z, double[] res);

	/**
	 * 
	 * @param z
	 * @return f^{-1}(z)
	 */
	double invLink(double z);
	
	/**
	 * evalEst is thought of as inverselink(beta.x), so heuristicLink() should be an approximation of the forward link.
	 * However heuristicLink() should be generous on domain, and only needs to be approximate.  
	 * In the case for Poisson regression the link is log(), so the inverse link is exp() so the heuristic link should be something
	 * that looks like log() but doesn't freak out at non-positive numbers.  The heuristic link is to be used only to try and 
	 * find initial starts for the optimizer, it is legit to try heuristicLink() as identity (the heuristic just has to be safe, not 
	 * returning NaN or infinite, it doesn't have to be accurate). 
	 * @return
	 */
	double heuristicLink(double y);
}
