package com.mzlabs.fit;

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
		xTx = factory.newMatrix(n,n,false);
		xTy = new double[n];
	}

	/* (non-Javadoc)
	 * @see com.mzlabs.count.util.Fitter#addObservation(double[], double, double)
	 */
	@Override
	public void addObservation(final double[] x, final double y, final double wt) {
		final int n = xTx.rows();
		if(n!=x.length) {
			throw new IllegalArgumentException();
		}
		for(int i=0;i<n;++i) {
			final double xi = x[i];
			xTy[i] += wt*xi*y;
			for(int j=0;j<n;++j) {
				final double xj = x[j];
				xTx.set(i,j,xTx.get(i, j)+wt*xi*xj);
			}
		}
	}
	
	/* (non-Javadoc)
	 * @see com.mzlabs.count.util.Fitter#solve()
	 */
	@Override
	public double[] solve() {
		final int n = xTx.rows();
		final double epsilon = 1.0e-5;
		final double[] xTxii = new double[n+1];
		for(int i=0;i<n;++i) {
			xTxii[i] = xTx.get(i,i);
			xTx.set(i,i,xTxii[i]+epsilon);  // Ridge term
		}
		final double[] soln = xTx.solve(xTy);
		for(int i=0;i<n;++i) {
			xTx.set(i,i,xTxii[i]);
		}
		return soln;
	}
	
	/* (non-Javadoc)
	 * @see com.mzlabs.count.util.Fitter#predict(double[], double[])
	 */
	public double predict(final double[] soln, final double[] x) {
		final int n = soln.length;
		if((n!=x.length)||(n!=soln.length)) {
			throw new IllegalArgumentException();
		}
		double sum = 0.0;
		for(int i=0;i<n;++i) {
			sum += x[i]*soln[i];
		}
		return sum;
	}
}
