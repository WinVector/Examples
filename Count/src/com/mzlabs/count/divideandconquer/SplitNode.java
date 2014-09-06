package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.Map;

import com.mzlabs.count.IntVec;
import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.ZeroOneCounter;

final class SplitNode implements NonNegativeIntegralCounter {
	private final NonNegativeIntegralCounter leftSubSystem;
	private final NonNegativeIntegralCounter rightSubSystem;
	private final int[][] A;
	private final boolean[][] usesRow;
	private final int[] entangledRows;
	private final Map<IntVec,BigInteger> cache = new HashMap<IntVec,BigInteger>(1000);
	
	public SplitNode(final int[][] A, final boolean[][] usesRow,
			final NonNegativeIntegralCounter leftSubSystem,
			final NonNegativeIntegralCounter rightSubSystem) {
		this.A = A;
		this.usesRow = usesRow;
		this.leftSubSystem = leftSubSystem;
		this.rightSubSystem = rightSubSystem;
		final int m = A.length;
		int nEntangled = 0;
		for(int i=0;i<m;++i) {
			if(usesRow[0][i]&&usesRow[1][i]) {
				++nEntangled;
			}
		}
		entangledRows = new int[nEntangled];
		nEntangled = 0;
		for(int i=0;i<m;++i) {
			if(usesRow[0][i]&&usesRow[1][i]) {
				entangledRows[nEntangled] = i;
				++nEntangled;
			}
		}
	}

	@Override
	public BigInteger countNonNegativeSolutions(final int[] b) {
		final IntVec key = new IntVec(b);
		BigInteger count = cache.get(key);
		if(null==count) {
			final int nEntangled = entangledRows.length;
			final int[] bound = new int[nEntangled];
			for(int ii=0;ii<nEntangled;++ii) {
				bound[ii] = b[entangledRows[ii]];
			}
			final IntVec bdE = new IntVec(bound);
			final int m = b.length;
			final  int[] counter = new int[nEntangled];
			final int[] b1 = new int[m];
			final int[] b2 = new int[m];
			for(int i=0;i<m;++i) {
				if(usesRow[0][i]) {
					b1[i] = b[i];
				}
				if(usesRow[1][i]) {
					b2[i] = b[i];
				}
			}
			count = BigInteger.ZERO;
			do {
				for(int ii=0;ii<nEntangled;++ii) {
					final int i = entangledRows[ii];
					b1[i] = counter[ii];
					b2[i] = b[i] - counter[ii];
				}
				// add sub1*sub2 terms, but try to avoid calculating sub(i) if sub(1-i) is obviously zero
				final BigInteger sub1 = leftSubSystem.countNonNegativeSolutions(b1);
				if(sub1.compareTo(BigInteger.ZERO)>0) {
					final BigInteger sub2 = rightSubSystem.countNonNegativeSolutions(b2);
					if(sub2.compareTo(BigInteger.ZERO)>0) {
						count = count.add(sub1.multiply(sub2));
					}
				}
			} while(bdE.advanceLE(counter));
			if(DivideAndConquerCounter.debug) {
				final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b);
				if(check.compareTo(count)!=0) {
					throw new IllegalStateException("got wrong answer");
				}
			}
			cache.put(key,count);
		}
		return count;
	}
	
	@Override
	public String toString() {
		return "split(" + A.length + "," + A[0].length + ";" + leftSubSystem + "," + rightSubSystem + ")";
	}
}
