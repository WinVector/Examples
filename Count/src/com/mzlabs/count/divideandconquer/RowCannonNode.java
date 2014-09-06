package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;

import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.ZeroOneCounter;
import com.mzlabs.count.divideandconquer.IntMat.RowDescription;

/**
 * Map A to a cannonical A with no zero rows, no duplicate rows and rows in a canonical order.
 * @author johnmount
 *
 */
final class RowCannonNode implements NonNegativeIntegralCounter {
	private final int[][] A;
	private final RowDescription[] rowDescr;
	private final NonNegativeIntegralCounter underlying;
	
	RowCannonNode(final int[][] A, final RowDescription[] rowDescr, final NonNegativeIntegralCounter underlying) {
		this.A = A;
		this.rowDescr = rowDescr;
		this.underlying = underlying;
	}
	
	
	@Override
	public BigInteger countNonNegativeSolutions(final int[] b) {
		// check if b obeys the implied symmetries of the homomorphism
		BigInteger count = null;
		for(final RowDescription di: rowDescr) {
			if(di.isZeroRow) {
				if(b[di.origIndex]!=0) {
					count = BigInteger.ZERO;
					break;
				}
			}
			if(di.matchingOldIndex>=0) {
				if(b[di.origIndex]!=b[di.matchingOldIndex]) {
					count = BigInteger.ZERO;
					break;
				}
			}
		}
		if(null!=count) {
			if(DivideAndConquerCounter.debug) {
				final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b);
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
			final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b);
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
