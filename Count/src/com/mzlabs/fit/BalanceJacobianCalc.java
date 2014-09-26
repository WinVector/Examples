package com.mzlabs.fit;

public interface BalanceJacobianCalc {
	/**
	 * 
	 * @param obs
	 * @param beta beta.length==obs.x.length+1
	 * @return balance eqns and Jacobian coefficients of underlying loss function for parametes beta with respect to datum obs
	 */
	BalanceJacobianCoef calc(Obs obs, double[] beta);
	
	/**
	 * 
	 * @param beta
	 * @param x x.length==beta.length-1 (last beta is the coefficient matchng an implicit constant term by convention)
	 * @return the estimate of y given parameters beta and datum x
	 */
	double evalEst(double[] beta, double[] x);
}
