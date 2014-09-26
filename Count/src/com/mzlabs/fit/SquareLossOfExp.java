package com.mzlabs.fit;

import java.util.Arrays;

import com.winvector.linalg.colt.ColtMatrix;

/**
 * sum(y-e^{x.dot(beta)})^2 not a regression (doesn't get expected values right)
 * @author johnmount
 *
 */
public class SquareLossOfExp implements VectorFnWithGradAndHessian {
	@Override
	public double evalEst(final double[] beta, final double[] x) {
		return Math.exp(Obs.dot(beta,x));
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
		double err = 0.0;
		for(final Obs obsi: obs) {
			final double ebx = evalEst(beta,obsi.x);
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

}
