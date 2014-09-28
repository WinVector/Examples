package com.mzlabs.fit;

import java.util.Arrays;

import com.winvector.linalg.colt.ColtMatrix;

public final class ExpectationAndSqLoss implements VectorFnWithJacobian {
	public final Link link;
	
	public ExpectationAndSqLoss(final Link link) {
		this.link = link;
	}

	public static double dotNE(double[] beta, double[] x) {
		final int n = x.length;
		if(n+1!=beta.length) {
			throw new IllegalArgumentException();
		}
		double bx = 0.0;
		for(int i=0;i<n;++i) {
			bx += beta[i]*x[i];
		}
		return bx;
	}
	
	@Override
	public double evalEst(double[] beta, double[] x) {
		return link.invLink(dotNE(beta,x));
	}

	@Override
	public double heuristicLink(final double y) {
		return link.heuristicLink(y);
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
		final double[] f = new double[3];
		for(final Obs obsi: obs) {
			final double lambda = beta[dim-1];
			final double bx = dotNE(beta,obsi.x);
			link.invLink(bx,f);
			{ // i,j < dim-1 case
				final double balCoef = obsi.wt*(2*f[0]-2*obsi.y+lambda)*f[1];
				final double jacCoef = obsi.wt*(2*f[1]*f[1] + (2*f[0]-2*obsi.y+lambda)*f[2]);
				for(int i=0;i<dim-1;++i) {
					final double xi = obsi.x[i];
					balance[i] += balCoef*xi;
					for(int j=0;j<dim-1;++j) {
						final double xj = obsi.x[j];
						final double jij = jacobian.get(i,j);
						jacobian.set(i,j,jij+xi*xj*jacCoef);
					}
				}
			}
			{ // i=dim-1, j<dim-1 case
				final int i = dim-1;
				balance[i] += obsi.wt*(f[0]-obsi.y);
				for(int j=0;j<dim-1;++j) {
					final double xj = obsi.x[j];
					final double jij = jacobian.get(i,j);
					jacobian.set(i,j,jij+obsi.wt*2*f[1]*xj);
				}
			}
			{ // i<dim-1, j=dim-1 case
				final int j = dim-1;
				for(int i=0;i<dim-1;++i) {
					final double xi = obsi.x[i];
					final double jij = jacobian.get(i,j);
					jacobian.set(i,j,jij+obsi.wt*f[1]*xi);
				}
			}
			// i==dim-1,j==dim-1 coef is zero
		}
	}

	@Override
	public int dim(final Obs obs) {
		return obs.x.length + 1;
	}
}
