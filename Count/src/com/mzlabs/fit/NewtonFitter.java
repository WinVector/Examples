package com.mzlabs.fit;

import java.util.ArrayList;

import com.winvector.linalg.LinalgFactory;
import com.winvector.linalg.colt.ColtMatrix;

public final class NewtonFitter implements Fitter {
	public final VectorFnWithJacobian link;
	public final ArrayList<Obs> obs = new ArrayList<Obs>();
	
	public NewtonFitter(final VectorFnWithJacobian link) {
		this.link = link;
	}
	
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
	 *  via Newton's method over balance (should equal zero) and Jacobian
	 * 
	 */
	
	@Override
	public double[] solve() {
		final LinalgFactory<ColtMatrix> factory = ColtMatrix.factory;
		final int dim = obs.get(0).x.length+1;
		// start at solution to log(y) ~ b.x
		final Fitter sf = new LinearFitter(dim-1);
		for(final Obs obsi: obs) {
			sf.addObservation(obsi.x, Math.log(Math.max(1.0,obsi.y)), obsi.wt);
		}
		final double[] beta = sf.solve();  // TODO: generalize this start position to use link info!
		final double[] balance = new double[dim];
		final ColtMatrix jacobian = factory.newMatrix(dim, dim, false);
		out:
		while(true) {
			link.balanceAndJacobian(obs,beta,balance,jacobian);
			// add regularization of overall optimization terms f(beta) = dot(beta,beta) (balance and jacobian from gradient and hessian of f() as follows)
			final double epsilon = 1.0e-5;
			for(int i=0;i<dim;++i) {
				balance[i] += 2*epsilon*beta[i];
				jacobian.set(i,i,jacobian.get(i,i)+2*epsilon);
			}
			double absGrad = 0.0;
			for(final double gi: balance) {
				absGrad += Math.abs(gi);
			}
			if(Double.isInfinite(absGrad)||Double.isNaN(absGrad)||(absGrad<=1.0e-8)) {
				break out;
			}
			try {
				// neaten up system a touch before solving
				double totAbs = 0.0;
				for(int i=0;i<dim;++i) {
					for(int j=0;j<dim;++j) {
						totAbs += Math.abs(jacobian.get(i,j));
					}
				}
				if(Double.isInfinite(totAbs)||Double.isNaN(totAbs)||(totAbs<=1.0e-8)) {
					break out;
				}
				final double scale = (dim*dim)/totAbs;
				for(int i=0;i<dim;++i) {
					balance[i] *= scale;
					for(int j=0;j<dim;++j) {
						jacobian.set(i,j,jacobian.get(i,j)*scale);
					}
				}
				final double[] delta = jacobian.solve(balance);
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
				if(deltaAbs<=1.0e-10) {
					break out;
				}
			} catch (Exception ex) {
				break out;
			}
		}
		return beta;
	}
}
