package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;

import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.divideandconquer.IntMat.RowDescription;
import com.mzlabs.count.zeroone.ZeroOneCounter;

/**
 * Map A to a cannonical A with no zero rows, no duplicate rows and rows in a canonical order.
 * @author johnmount
 *
 */
final class RowCannonNode implements NonNegativeIntegralCounter {
	private final int[][] A;
	private final RowDescription[] rowDescr;
	private final NonNegativeIntegralCounter underlying;
	private final boolean zeroOne;
	
	RowCannonNode(final int[][] A, final RowDescription[] rowDescr, final NonNegativeIntegralCounter underlying, final boolean zeroOne) {
		this.A = A;
		this.rowDescr = rowDescr;
		this.underlying = underlying;
		this.zeroOne = zeroOne;
	}
	
	
	@Override
	public BigInteger countNonNegativeSolutions(final int[] b) {
		// check if b obeys the implied symmetries of the homomorphism
		final int m = b.length;
		BigInteger count = null;
		for(final RowDescription di: rowDescr) {
			if(di.newIndex<0) {
				double impliedB = 0.0;
				for(int j=0;j<m;++j) {
					impliedB += di.soln[j]*b[j];
				}
				if(Math.abs(impliedB-b[di.origIndex])>1.0e-6) {
					count = BigInteger.ZERO;
					break;
				}
			}
		}
		if(null!=count) {
			if(DivideAndConquerCounter.debug) {
				final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b,zeroOne);
				if(check.compareTo(count)!=0) {
					throw new IllegalStateException("got wrong answer");
				}
			}
			return count;
		}
		// delegate the counting to underlying
		final int[] b2 = IntMat.mapVector(rowDescr,b);
		count = underlying.countNonNegativeSolutions(b2);
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
		return "(" + underlying + ")";
	}
}
