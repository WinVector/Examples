package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;

import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.util.IntMat;
import com.mzlabs.count.util.IntMat.RowDescription;
import com.mzlabs.count.zeroone.ZeroOneCounter;

/**
 * Map A to a cannonical A with no zero rows, no duplicate rows and rows in a canonical order.
 * @author johnmount
 *
 */
final class RowCannonNode implements NonNegativeIntegralCounter {
	private final int[][] A;
	private final int m;
	private final int rowRank;
	private final RowDescription[] rowDescr;
	private final NonNegativeIntegralCounter underlying;
	private final boolean zeroOne;
	
	RowCannonNode(final int[][] A, final RowDescription[] rowDescr, final NonNegativeIntegralCounter underlying, final boolean zeroOne) {
		this.A = A;
		this.rowDescr = rowDescr;
		this.underlying = underlying;
		this.zeroOne = zeroOne;
		m = A.length;
		int nBasis = 0;
		for(final RowDescription di: rowDescr) {
			if(di.newIndex>=0) {
				++nBasis;
			}
		}
		rowRank = nBasis;
	}
	
	@Override
	public boolean obviouslyEmpty(final int[] b) {
		// check if b obeys the implied symmetries of the homomorphism
		for(final RowDescription di: rowDescr) {
			if(di.newIndex<0) {
				double impliedB = 0.0;
				for(int j=0;j<m;++j) {
					impliedB += di.soln[j]*b[j];
				}
				if(Math.abs(impliedB-b[di.origIndex])>1.0e-6) {
					return true;
				}
			}
		}
		// Could delegate, but not much point is the obviouslyEmpty() is mostly to get info from this node
		return false;
	}
	
	@Override
	public BigInteger countNonNegativeSolutions(final int[] b) {
		if(obviouslyEmpty(b)) {
			if(DivideAndConquerCounter.debug) {
				final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b,zeroOne);
				if(check.compareTo(BigInteger.ZERO)!=0) {
					throw new IllegalStateException("got wrong answer");
				}
			}
			return BigInteger.ZERO;
		}
		// delegate the counting to underlying
		final int[] b2 = IntMat.mapVector(rowDescr,b);
		final BigInteger count = underlying.countNonNegativeSolutions(b2);
		if(DivideAndConquerCounter.debug) {
			final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b,zeroOne);
			if(check.compareTo(count)!=0) {
				throw new IllegalStateException("got wrong answer");
			}
		}
		return count;
	}
	
	@Override
	public String toString() {
		return "{" + m + "\\" + rowRank + "," + underlying + "}";
	}

	@Override
	public long cacheSize() {
		return underlying.cacheSize();
	}

	@Override
	public void clearCache() {
		underlying.clearCache();
	}
}
