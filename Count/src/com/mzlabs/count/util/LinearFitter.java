package com.mzlabs.count.util;

import com.winvector.linalg.LinalgFactory;
import com.winvector.linalg.colt.ColtMatrix;


/**
 * Fit y ~ a + b.x (least squares)
 * @author johnmount
 *
 */
public final class LinearFitter implements Fitter {
	private final ColtMatrix xTx;
	private final double[] xTy;
	
	/**
	 * 
	 * @param n dimension of x-vectors
	 */
	public LinearFitter(final int n) {
		final LinalgFactory<ColtMatrix> factory = ColtMatrix.factory;
		xTx = factory.newMatrix(n+1,n+1,false);
		xTy = new double[n+1];
	}

	/* (non-Javadoc)
	 * @see com.mzlabs.count.util.Fitter#addObservation(double[], double, double)
	 */
	@Override
	public void addObservation(final double[] x, final double y, final double wt) {
		final int n = xTx.rows()-1;
		if(n!=x.length) {
			throw new IllegalArgumentException();
		}
		for(int i=0;i<=n;++i) {
			final double xi = i<n?x[i]:1.0;
			xTy[i] += wt*xi*y;
			for(int j=0;j<=n;++j) {
				final double xj = j<n?x[j]:1.0;
				xTx.set(i,j,xTx.get(i, j)+wt*xi*xj);
			}
		}
	}
	
	/* (non-Javadoc)
	 * @see com.mzlabs.count.util.Fitter#solve()
	 */
	@Override
	public double[] solve() {
		final int n = xTx.rows()-1;
		final double epsilon = 1.0e-5;
		final double[] xTxii = new double[n+1];
		for(int i=0;i<=n;++i) {
			xTxii[i] = xTx.get(i,i);
			xTx.set(i,i,xTxii[i]+epsilon);  // Ridge term
		}
		final double[] soln = xTx.solve(xTy);
		for(int i=0;i<=n;++i) {
			xTx.set(i,i,xTxii[i]);
		}
		return soln;
	}
	
	/* (non-Javadoc)
	 * @see com.mzlabs.count.util.Fitter#predict(double[], double[])
	 */
	@Override
	public double predict(final double[] soln, final double[] x) {
		final int n = soln.length-1;
		if((n!=x.length)||(n+1!=soln.length)) {
			throw new IllegalArgumentException();
		}
		double sum = 0.0;
		for(int i=0;i<=n;++i) {
			final double xi = i<n?x[i]:1.0;
			sum += xi*soln[i];
		}
		return sum;
	}
}
