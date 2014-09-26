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
	 * @param x x.length==beta.length-1 (last beta is the coefficient matchng an implicit constant term by convention)
	 * @return the estimate of y given parameters beta and datum x
	 */
	public double evalEst(double[] beta, double[] x);
	
	/**
	 * f() is a vector function, return the function eval in balance (solving for f(x)==0) and the Jacobian in jacobian
	 * @param obs
	 * @param beta
	 * @param balance grad.length==beta.length
	 * @param jacobian jacobian.rows()==jacobian.cols()==beta.length
	 */
	public void balanceAndJacobian(Iterable<Obs> obs, double[] beta, double[] balance, ColtMatrix jacobian);
}
