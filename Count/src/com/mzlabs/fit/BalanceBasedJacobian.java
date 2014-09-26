package com.mzlabs.fit;


/**
 * This returns a set of equations that should be zero (what we have been calling a gradient) and the Jacobian of these equations (what we
 * have been calling the hessian).  We don't care if there is an underlying function that we are the gradient of.  And if we are using this
 * to build a GLM link we are assuming the probability model is such that the gradient of log(P(y|f(obs.dot(beta)))) is our given balance equations.
 * Note we only use the first two positions of the link.
 * @author johnmount
 *
 */
public final class BalanceBasedJacobian implements BalanceJacobianCalc {
	public final Link link;
	
	public BalanceBasedJacobian(final Link link) {
		this.link = link;
	}

	@Override
	public BalanceJacobianCoef calc(final Obs obs, final double[] beta) {
		final double[] z = new double[3];
		final double bx = obs.dot(beta);
		link.invLink(bx,z);
		final double balanceCoef = obs.wt*(obs.y-z[0]);  // hard coded Poisson gradient component
		final double jacobianCoef = obs.wt*(-z[1]);
		return new BalanceJacobianCoef(balanceCoef,jacobianCoef);
	}

	@Override
	public double evalEst(final double[] beta, final double[] x) {
		return link.invLink(Obs.dot(beta,x));
	}

	public static final BalanceBasedJacobian poissonJacobian = new BalanceBasedJacobian(LinkBasedGradHess.LogLink);
	public static GLMModel poissonLink = new GLMModel(poissonJacobian);
}
