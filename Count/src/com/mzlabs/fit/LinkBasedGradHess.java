package com.mzlabs.fit;

/**
 * calculate the scalar portion of gradient and hessian (balance and jacobian in larger scope) directly using
 * link and probability model
 * @author johnmount
 *
 */
public final class LinkBasedGradHess implements BalanceJacobianCalc {
	public final ProbYGivenZ prob;
	public final Link link;
	
	public LinkBasedGradHess(final ProbYGivenZ prob, final Link link) {
		this.prob = prob;
		this.link = link;
	}

	private static double sq(final double z) {
		return z*z;
	}
	
	@Override
	public BalanceJacobianCoef calc(Obs obs, double[] beta) {
		final double[] p = new double[3];
		final double[] z = new double[3];
		final double bx = obs.dot(beta);
		link.invLink(bx,z);
		prob.eval(obs.y,z[0],p);
		final double gradCoef = obs.wt*z[1]*p[1]/p[0];
		final double hessCoef = obs.wt*(-sq(z[1])*sq(p[1])/sq(p[0]) + sq(z[1])*p[2]/p[0] + z[2]*p[1]/p[0]);
		return new BalanceJacobianCoef(gradCoef,hessCoef);
	}
	
	@Override
	public double evalEst(double[] beta, double[] x) {
		return link.invLink(Obs.dot(beta,x));
	}
	
	@Override
	public double heuristicLink(final double y) {
		return link.heuristicLink(y);
	}
	
	
	
	
	public static final ProbYGivenZ poissonProbability = new ProbYGivenZ() {
		@Override
		public void eval(final double y, final double z, final double[] res) {
			if(y>0) {
				final double fyz = Math.exp(y*Math.log(z)-z); // ignoring a gamma(y+1) term here
				res[0] = fyz;
				res[1] = fyz*(y/z-1);
				res[2] = fyz*((y/z-1)*(y/z-1)-y/(z*z));
			} else {
				final double fyz = Math.exp(-z); // ignoring a gamma(y+1) term here
				res[0] = fyz;
				res[1] = -fyz;
				res[2] = fyz;
			}
		}
	};
	
	public static final Link logLink = new Link() {
		@Override
		public void invLink(final double z, final double[] res) {
			final double ez = Math.exp(z);
			res[0] = ez;
			res[1] = ez;
			res[2] = ez;
		}
		@Override
		public double invLink(final double z) {
			return Math.exp(z);
		}
		@Override
		public double heuristicLink(double y) {
			return Math.log(Math.abs(y)+1.0); // near log(y), but well behaved
		}
	};
	
	
	public static final LinkBasedGradHess poissonGradHess = new LinkBasedGradHess(poissonProbability,logLink);
	public static GLMModel poissonLink = new GLMModel(poissonGradHess);
}
