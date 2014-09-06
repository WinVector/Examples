package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;

import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.ZeroOneCounter;
import com.winvector.linalg.LinalgFactory;
import com.winvector.linalg.colt.ColtMatrix;

final class TerminalNode implements NonNegativeIntegralCounter {
	private final static LinalgFactory<ColtMatrix> factory = ColtMatrix.factory;
	private static final double epsilon = 1.0e-8;
	private final int[][] A;
	private final ColtMatrix fwd;
	private final ColtMatrix inv;
	

	private TerminalNode(final int[][] A, final ColtMatrix fwd, final ColtMatrix inv) {
		this.A = A;
		this.fwd = fwd;
		this.inv = inv;
	}
	
	/**
	 * For matrices that are full column rank A x = b has one solution, so we 
	 * can solve via linear algebra and then check non-negativity.  So there
	 * are always zero or one solutions in this case.
	 * @param A
	 * @return
	 */
	public static TerminalNode tryToBuildTerminalNode(final int[][] A) {
		final int m = A.length;
		final int n = A[0].length;
		if(n>m) {
			return null; // more columns than rows, can't be full column rank
		}
		final ColtMatrix amat = factory.newMatrix(m,n,false);
		final ColtMatrix amatT = factory.newMatrix(n,m,false);
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				amat.set(i,j,A[i][j]);
				amatT.set(j,i,A[i][j]);
			}
		}
		final ColtMatrix aTa = amatT.multMat(amat);
		try {
			final ColtMatrix aTaI = aTa.inverse();
			boolean goodMat = true;
			final ColtMatrix check = aTaI.multMat(aTa);
			final int k = check.rows();
			for(int i=0;(i<k)&&(goodMat);++i) {
				for(int j=0;(j<k)&&(goodMat);++j) {
					if(i==j) {
						if(Math.abs(check.get(i,j)-1.0)>epsilon) {
							goodMat = false;
						}
					} else {
						if(Math.abs(check.get(i,j))>epsilon) {
							goodMat = false;
						}
					}
				}
			}
			if(goodMat) {
				return new TerminalNode(A,amat,aTaI.multMat(amatT));
			}
		} catch (Exception ex) {
		}
		return null;
	}
	
	@Override
	public BigInteger countNonNegativeSolutions(final int[] b) {
		final int m = fwd.rows();
		final double[] bD = new double[m];
		for(int i=0;i<m;++i) {
			bD[i] = b[i];
		}
		final double[] soln = inv.mult(bD);
		for(final double si: soln) {
			if((si<-epsilon)||(Math.abs(si-Math.round(si))>epsilon)) {
				final BigInteger count = BigInteger.ZERO;
				if(DivideAndConquerCounter.debug) {
					final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b);
					if(check.compareTo(count)!=0) {
						throw new IllegalStateException("got wrong answer");
					}
				}
				return count;
			}
		}
		final double[] recovered = fwd.mult(soln);
		for(int i=0;i<m;++i) {
			if(Math.abs(recovered[i]-b[i])>epsilon) {
				final BigInteger count = BigInteger.ZERO;
				if(DivideAndConquerCounter.debug) {
					final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b);
					if(check.compareTo(count)!=0) {
						throw new IllegalStateException("got wrong answer");
					}
				}
				return count;
			}
		}
		final BigInteger count = BigInteger.ONE;
		if(DivideAndConquerCounter.debug) {
			final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b);
			if(check.compareTo(count)!=0) {
				throw new IllegalStateException("got wrong answer");
			}
		}
		return count;
	}
	
	@Override
	public String toString() {
		return "terminal[" + A.length + "," + A[0].length + "]";
	}
}
