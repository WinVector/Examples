package com.mzlabs.fit;

import java.util.Arrays;

import com.winvector.linalg.colt.ColtMatrix;

/**
 * sum(y-e^{x.dot(beta)})^2 not a regression (doesn't get expected values right)
 * @author johnmount
 *
 */
public class SquareLossOfExp implements VectorFnWithJacobian {
	@Override
	public double evalEst(final double[] beta, final double[] x) {
		return Math.exp(Obs.dot(beta,x));
	}

	@Override
	public double heuristicLink(final double y) {
		return Math.log(Math.abs(y)+1.0); // near log(y), but well behaved
	}


	@Override
	public void balanceAndJacobian(final Iterable<Obs> obs, final double[] beta,
			final double[] balance, final ColtMatrix jacobian) {
		final int dim = beta.length;
		Arrays.fill(balance,0.0);
		for(int i=0;i<dim;++i) {
			for(int j=0;j<dim;++j) {
				jacobian.set(i,j,0.0);
			}
		}
		for(final Obs obsi: obs) {
			final double ebx = evalEst(beta,obsi.x);
			final double diff = obsi.y-ebx;
			final double gradCoef = -2*diff*ebx*obsi.wt;
			final double hessCoef = -2*(obsi.y-2*ebx)*ebx*obsi.wt;
			for(int i=0;i<dim;++i) {
				final double xi = i<dim-1?obsi.x[i]:1.0;
				balance[i] += gradCoef*xi;
				for(int j=0;j<dim;++j) {
					final double xj = j<dim-1?obsi.x[j]:1.0;
					final double hij = jacobian.get(i,j);
					jacobian.set(i,j,hij+xi*xj*hessCoef);
				}
			}
		}
	}
}
