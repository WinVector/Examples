package com.mzlabs.fit;

import com.winvector.linalg.colt.ColtMatrix;

/**
 * Model f() a loss function of a parameter setting beta with respect to data (obs)
 * @author johnmount
 *
 */
public interface VectorFnWithJacobian {
	/**
	 * 
	 * @param beta
	 * @param x x.length==beta.length (last beta is the coefficient matchng an implicit constant term by convention)
	 * @return the estimate of y given parameters beta and datum x
	 */
	double evalEst(double[] beta, double[] x);

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

	/**
	 * f() is a vector function, return the function eval in balance (solving for f(x)==0) and the Jacobian in jacobian
	 * @param obs
	 * @param beta
	 * @param balance grad.length==beta.length
	 * @param jacobian jacobian.rows()==jacobian.cols()==beta.length
	 */
	void balanceAndJacobian(Iterable<Obs> obs, double[] beta, double[] balance, ColtMatrix jacobian);
}
