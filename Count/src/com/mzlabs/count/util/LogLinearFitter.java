package com.mzlabs.count.util;

import java.util.ArrayList;
import java.util.Arrays;


import com.winvector.linalg.LinalgFactory;
import com.winvector.linalg.colt.ColtMatrix;

public final class LogLinearFitter implements Fitter {
	public static final class Obs {
		public final double[] x;
		public final double y;
		public final double wt;
		
		public Obs(final double[] x, final double y, final double wt) {
			this.x = Arrays.copyOf(x,x.length);
			this.y = y;
			this.wt = wt;
		}
		
		@Override
		public String toString() {
			final StringBuilder b = new StringBuilder();
			b.append("" + wt + ":[");
			for(final double xi:x) {
				b.append(" " + xi);
			}
			b.append(" ]-> " + y);
			return b.toString();
		}
	}
	
	private final ArrayList<Obs> obs = new ArrayList<Obs>();
	
	
	@Override
	public void addObservation(final double[] x, final double y, final double wt) {
		if(!obs.isEmpty()) {
			final int n = obs.get(0).x.length;
			if(n!=x.length) {
				throw new IllegalArgumentException();
			}
		}
		final Obs obsi = new Obs(x,y,wt);
		obs.add(obsi);
	}
	
	/**
	 *  minimize sum_i wt[i] (e^{beta.x[i]} - y[i])^2
	 *  via Newton's method over gradient (should equal zero) and Hessian (Jacobian of vector eqn)
	 * 
	 */
	
	private static double dot(final double[] soln, final double[] x) {
		final int n = x.length;
		double sum = 0.0;
		for(int i=0;i<=n;++i) {
			final double xi = i<n?x[i]:1.0;
			sum += xi*soln[i];
		}
		return sum;
	}
	
	private double errAndGradAndHessian(final double[] beta, final double[] grad, final ColtMatrix hessian) {
		final int dim = beta.length;
		Arrays.fill(grad,0.0);
		for(int i=0;i<dim;++i) {
			for(int j=0;j<dim;++j) {
				hessian.set(i,j,0.0);
			}
		}
		double err = 0.0;
		for(final Obs obsi: obs) {
			final double ebx = Math.exp(dot(beta,obsi.x));
			final double diff = obsi.y-ebx;
			err += diff*diff;
			final double gradCoef = -2*diff*ebx*obsi.wt;
			final double hessCoef = -2*(obsi.y-2*ebx)*ebx*obsi.wt;
			for(int i=0;i<dim;++i) {
				final double xi = i<dim-1?obsi.x[i]:1.0;
				grad[i] += gradCoef*xi;
				for(int j=0;j<dim;++j) {
					final double xj = j<dim-1?obsi.x[j]:1.0;
					final double hij = hessian.get(i,j);
					hessian.set(i,j,hij+xi*xj*hessCoef);
				}
			}
		}
		return err;
	}

	@Override
	public double[] solve() {
		final LinalgFactory<ColtMatrix> factory = ColtMatrix.factory;
		final int dim = obs.get(0).x.length+1;
		// start at solution to log(y) ~ b.x
		final Fitter sf = new LinearFitter(dim-1);
		for(final Obs obsi: obs) {
			sf.addObservation(obsi.x, Math.log(Math.max(1.0,obsi.y)), obsi.wt);
		}
		final double[] beta = sf.solve();
		double bestErr = Double.POSITIVE_INFINITY;
		double[] bestBeta = Arrays.copyOf(beta,beta.length);
		final double[] grad = new double[dim];
		final ColtMatrix hessian = factory.newMatrix(dim, dim, false);
		int nFails = 0;
		out:
		while(true) {
			final double err = errAndGradAndHessian(beta,grad,hessian);
			if((null==bestBeta)||(err<bestErr)) {
				bestErr = err;
				bestBeta = Arrays.copyOf(beta,beta.length);
				nFails = 0;
			} else {
				++nFails;
				if(nFails>=5) {
					break out;
				}
			}
			double absGrad = 0.0;
			for(final double gi: grad) {
				absGrad += Math.abs(gi);
			}
			if(Double.isInfinite(absGrad)||Double.isNaN(absGrad)||(absGrad<=1.0e-8)) {
				break out;
			}
			try {
//				// neaten up system a touch before solving
//				double totAbs = 0.0;
//				for(int i=0;i<dim;++i) {
//					for(int j=0;j<dim;++j) {
//						totAbs += Math.abs(hessian.get(i,j));
//					}
//				}
//				if(Double.isInfinite(totAbs)||Double.isNaN(totAbs)||(totAbs<=1.0e-8)) {
//					break out;
//				}
//				final double scale = (dim*dim)/totAbs;
//				for(int i=0;i<dim;++i) {
//					grad[i] *= scale;
//					for(int j=0;j<dim;++j) {
//						hessian.set(i,j,hessian.get(i,j)*scale);
//					}
//				}
//				for(int i=0;i<dim;++i) {
//					hessian.set(i,i,hessian.get(i,i)+1.e-5); // Ridge term
//				}
				final double[] delta = hessian.solve(grad);
				for(final double di: delta) {
					if(Double.isNaN(di)||Double.isNaN(di)) {
						break out;
					}
				}
				double deltaAbs = 0.0;
				for(int i=0;i<dim;++i) {
					beta[i] -= delta[i];
					deltaAbs += Math.abs(delta[i]);
				}
				if(deltaAbs<=1.0e-7) {
					break out;
				}
			} catch (Exception ex) {
				break out;
			}
		}
		return bestBeta;
	}

	@Override
	public double predict(final double[] soln, final double[] x) {
		final int n = obs.get(0).x.length;
		if((n!=x.length)||(n+1!=soln.length)) {
			throw new IllegalArgumentException();
		}
		return Math.exp(dot(soln,x));
	}
}
