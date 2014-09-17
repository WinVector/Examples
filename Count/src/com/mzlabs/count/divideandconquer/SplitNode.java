package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;

import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.op.IntFunc;
import com.mzlabs.count.op.IntVecFn;
import com.mzlabs.count.op.Reducer;
import com.mzlabs.count.op.Sequencer;
import com.mzlabs.count.op.SolnCache;
import com.mzlabs.count.op.impl.SimpleSum;
import com.mzlabs.count.op.impl.ThreadedSum;
import com.mzlabs.count.op.iter.RangeIter;
import com.mzlabs.count.op.iter.SeqLE;
import com.mzlabs.count.util.IntVec;

final class SplitNode implements NonNegativeIntegralCounter,IntVecFn {
	private final NonNegativeIntegralCounter leftSubSystem;
	private final NonNegativeIntegralCounter rightSubSystem;
	private final int[][] A;
	private final int m;
	private final int n;
	private final int nEntangled;
	private final boolean[][] usesRow;
	private final int[] entangledRows;
	private final boolean runParallel;
	private final boolean zeroOne;
	private final SolnCache cache = new SolnCache();
	
	public SplitNode(final int[][] A, final boolean[][] usesRow, final boolean runParallel,
			final NonNegativeIntegralCounter leftSubSystem,
			final NonNegativeIntegralCounter rightSubSystem,
			final boolean zeroOne) {
		this.A = A;
		this.usesRow = usesRow;
		this.runParallel = runParallel;
		this.leftSubSystem = leftSubSystem;
		this.rightSubSystem = rightSubSystem;
		this.zeroOne = zeroOne;
		m = A.length;
		n = A[0].length;
		int nE = 0;
		for(int i=0;i<m;++i) {
			if(usesRow[0][i]&&usesRow[1][i]) {
				++nE;
			}
		}
		nEntangled = nE;
		//System.out.println("split node m:" + m + ", n: " + A[0].length + ", nEntangled:" + nEntangled +
		//		", rank:" + IntMat.rowBasis(A).length);
		entangledRows = new int[nEntangled];
		nE = 0;
		for(int i=0;i<m;++i) {
			if(usesRow[0][i]&&usesRow[1][i]) {
				entangledRows[nE] = i;
				++nE;
			}
		}
	}
	
	@Override
	public boolean obviouslyEmpty(final int[] bIn) {
		return false;
	}
	
	@Override
	public BigInteger eval(final IntVec b) {
		final int[] bound = new int[nEntangled];
		for(int ii=0;ii<nEntangled;++ii) {
			final int i = entangledRows[ii];
			bound[ii] = b.get(i);
			if(zeroOne) {
				int rowSum = 0;
				for(int j=0;j<n;++j) {
					rowSum += A[i][j];
				}
				bound[ii] = Math.min(bound[ii],rowSum);
			}
		}
		final IntVec bdE = new IntVec(bound);
		final Sequencer seq = new SeqLE(bdE,bdE.dim(),bdE.dim()-1);
		final IntFunc subF = new IntFunc() {
			@Override
			public BigInteger f(final int[] x) {
				final int lastVal = x[0];
				BigInteger accumulator = BigInteger.ZERO;
				final int[] b1 = new int[m];
				final int[] b2 = new int[m];
				for(int i=0;i<m;++i) {
					if(usesRow[0][i]) {
						b1[i] = b.get(i);
					}
					if(usesRow[1][i]) {
						b2[i] = b.get(i);
					}
				}
				final int[] counter = new int[nEntangled];
				counter[nEntangled-1] = lastVal;
				do {
					for(int ii=0;ii<nEntangled;++ii) {
						final int i = entangledRows[ii];
						b1[i] = counter[ii];
						b2[i] = b.get(i) - counter[ii];
					}
					// b1 + b2 == b
					// add sub1*sub2 terms, but try to avoid calculating sub(i) if sub(1-i) is obviously zero
					if((!leftSubSystem.obviouslyEmpty(b1))&&(!rightSubSystem.obviouslyEmpty(b2))) {
						final BigInteger sub1 = leftSubSystem.countNonNegativeSolutions(b1);
						if(sub1.compareTo(BigInteger.ZERO)>0) {
							final BigInteger sub2 = rightSubSystem.countNonNegativeSolutions(b2);
							if(sub2.compareTo(BigInteger.ZERO)>0) {
								final BigInteger term = sub1.multiply(sub2);
								accumulator = accumulator.add(term);
							}
						}
					}
				} while(seq.advance(counter));
				return accumulator;
			}
		};
		final Sequencer seqL = new RangeIter(0,bdE.get(nEntangled-1)+1);
		final Reducer summer = runParallel?new ThreadedSum():new SimpleSum();
		final BigInteger sum = summer.reduce(subF,seqL);
		return sum;
	}
	
	@Override
	public BigInteger countNonNegativeSolutions(final int[] b) {
		return cache.evalCached(this,new IntVec(b));
	}

	
	@Override
	public String toString() {
		return "split(" + A.length + "\\" + nEntangled + "," + n  + ";" + leftSubSystem + "," + rightSubSystem + ")";
	}
	
	@Override
	public long cacheSize() {
		return leftSubSystem.cacheSize() + rightSubSystem.cacheSize() + cache.size();
	}

	@Override
	public void clearCache() {
		leftSubSystem.clearCache();
		rightSubSystem.clearCache();
		cache.clear();
	}
}
