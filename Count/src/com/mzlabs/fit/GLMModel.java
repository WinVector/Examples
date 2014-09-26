package com.mzlabs.fit;

import java.util.Arrays;

import com.winvector.linalg.colt.ColtMatrix;

public class GLMModel implements VectorFnWithGradAndHessian {
	public final boolean debug;
	public final ProbYGivenZ prob;
	public final Link link;
	
	
	public GLMModel(final ProbYGivenZ prob, final Link link, final boolean debug) {
		this.prob = prob;
		this.link = link;
		this.debug = debug;
	}
	
	@Override
	public double evalEst(final double[] beta, final double[] x) {
		return link.invLink(Obs.dot(beta,x));
	}

	public Double checkGradCoef(final Obs obsi, final double[] beta) {
		return null;
	}
	
	public Double checkHessianCoef(final Obs obsi, final double[] beta) {
		return null;
	}
	
	public static final ProbYGivenZ PoissonProbability = new ProbYGivenZ() {
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
	public static final Link LogLink = new Link() {
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
	};
	
	public static GLMModel PoissonLink = new GLMModel(PoissonProbability,LogLink,false);
	public static GLMModel PoissonLinkDebug = new GLMModel(PoissonProbability,LogLink,true) {
		@Override
		public Double checkGradCoef(final Obs obsi, final double[] beta) {
			final double bx = obsi.dot(beta);
			return obsi.wt*(obsi.y-Math.exp(bx));  // hard coded Poisson gradient component
		}
		@Override
		public Double checkHessianCoef(final Obs obsi, final double[] beta) {
			final double bx = obsi.dot(beta);
			return obsi.wt*(-Math.exp(bx)); // hard coded Poisson hessian component
		}
	};


	private static double sq(final double z) {
		return z*z;
	}

	
	@Override
	public double lossAndGradAndHessian(final Iterable<Obs> obs, final double[] beta,
			final double[] grad, final ColtMatrix hessian) {
		final int dim = beta.length;
		Arrays.fill(grad,0.0);
		for(int i=0;i<dim;++i) {
			for(int j=0;j<dim;++j) {
				hessian.set(i,j,0.0);
			}
		}
		final double[] p = new double[3];
		final double[] z = new double[3];
		double sum = 0.0;
		for(final Obs obsi: obs) {
			final double bx = obsi.dot(beta);
			link.invLink(bx,z);
			prob.eval(obsi.y,z[0],p);
			sum += obsi.wt*Math.log(z[0]);
			final double gradScale = obsi.wt*z[1]*p[1]/p[0];
			final double hessCoef = obsi.wt*(-sq(z[1])*sq(p[1])/sq(p[0]) + sq(z[1])*p[2]/p[0] + z[2]*p[1]/p[0]);
			if(debug) {
				final Double gradP = checkGradCoef(obsi,beta);
				final Double hessP = checkHessianCoef(obsi,beta);
				if((null!=gradP)&&(Math.abs(gradScale-gradP)>=1.0e-6)) {
					throw new IllegalStateException("gradient checks didn't match");
				}
				if((null!=hessP)&&(Math.abs(hessCoef-hessP)>1.0e-6)) {
					throw new IllegalStateException("Hessian checks didn't match");
				}
			}
			for(int i=0;i<dim;++i) {
				final double xi = i<dim-1?obsi.x[i]:1.0;
				grad[i] += gradScale*xi;
				for(int j=0;j<dim;++j) {
					final double xj = j<dim-1?obsi.x[j]:1.0;
					final double hij = hessian.get(i,j);
					hessian.set(i,j,hij+xi*xj*hessCoef);
				}
			}
		}
		return sum;
	}



}
