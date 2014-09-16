package com.mzlabs.count.ctab;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.Date;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.divideandconquer.DivideAndConquerCounter;
import com.mzlabs.count.op.IntFunc;
import com.mzlabs.count.op.Reducer;
import com.mzlabs.count.op.impl.SimpleSum;
import com.mzlabs.count.op.impl.ThreadedSum;
import com.mzlabs.count.op.iter.OrderStepperTot;
import com.mzlabs.count.util.IntVec;
import com.mzlabs.count.zeroone.ZeroOneCounter;


public final class CTab {
	
	private static final class CPair {
		public final ContingencyTableProblem prob;
		public final NonNegativeIntegralCounter counter;
		
		public CPair(final ContingencyTableProblem prob, final NonNegativeIntegralCounter counter) {
			this.prob = prob;
			this.counter = counter;
		}
	}
	
	private final boolean runParallel;
	private final CPair[][] subCounters;
	
	public CTab(final int maxRowColSize, final boolean runParallel) {
		this.runParallel = runParallel;
		subCounters = new CPair[maxRowColSize+1][maxRowColSize+1];
	}
	
	
	/**
	 * count number of rowsCols by rowsCols contingency table fill-ins with all rows/columns summing to total
	 * @param rowsCols >0
	 * @param total
	 * @return
	 */
	public BigInteger countSqTables(final int rowsCols, final int total) {
		if(rowsCols<=0) {
			throw new IllegalArgumentException();
		}
		if(total<0) {
			return BigInteger.ZERO;
		}
		if((total==0)||(rowsCols==1)) {
			return BigInteger.ONE;
		}
		// now know rowsCols>1 and total>0, split into semi-regular tables
		final int n1 = rowsCols/2;
		final int n2 = rowsCols - n1;
		final int targetSum = n1*total;
		final OrderStepperTot stepper = new OrderStepperTot(rowsCols,total,targetSum);
		final IntFunc subF = new IntFunc() {
			@Override
			public BigInteger f(final int[] x) {
				final BigInteger xCount = countSemiTables(n1,total,x);
				if(xCount.compareTo(BigInteger.ZERO)>0) {
					final int[] y = new int[rowsCols];
					for(int i=0;i<rowsCols;++i) {
						y[i] = total - x[i];
					}
					Arrays.sort(y);
					final BigInteger yCount = countSemiTables(n2,total,y);
					if(yCount.compareTo(BigInteger.ZERO)>0) {
						final BigInteger nperm = stepper.nPerm(x);
						final BigInteger term = nperm.multiply(xCount).multiply(yCount);
						synchronized (this) {
							return term;
						}
					}
				}
				return BigInteger.ZERO;
			}
		};
		final Reducer summer = runParallel?new ThreadedSum():new SimpleSum();
		final BigInteger sum = summer.reduce(subF,stepper);
		return sum;
	}
	
	private CPair getSubCounter(final int nRows, final int nCols) {
		CPair counter = null;
		synchronized (subCounters) { // essentially serialized here
			counter = subCounters[nRows][nCols];
			if(null==counter) {
				final ContingencyTableProblem cp = new ContingencyTableProblem(nRows,nCols);
				final NonNegativeIntegralCounter cnt;
				if(nRows*nCols<=28) {
					cnt = new ZeroOneCounter(cp,true);
				} else {
					cnt = new DivideAndConquerCounter(cp,false,false,true);
				}
				counter = new CPair(cp,cnt);
				subCounters[nRows][nCols] = counter;
			}
		}
		return counter;
	}
	
	public String cacheSizesString() {
		synchronized (subCounters) {
			final StringBuilder b = new StringBuilder();
			b.append("{");
			for(int i=0;i<subCounters.length;++i) {
				for(int j=0;j<subCounters[i].length;++j) {
					final CPair counter = subCounters[i][j];
					if(null!=counter) {
						b.append(" [" + i + "," + j + "]:" + counter.counter.cacheSize());		
					}
				}
			}
			b.append(" }");
			return b.toString();
		}
	}
	
	public void clearCaches() {
		synchronized (subCounters) { 
			for(final CPair[] row: subCounters) {
				for(final CPair cij: row) {
					if(null!=cij) {
						cij.counter.clearCache();
					}
				}
			}
		}
	}

	/**
	 * count number of contingency table fill-ins with nCols (all summing to colBound) and rows summing to rowBounds 
	 * @param nCols >0
	 * @param colTotal >0
	 * @param rowBounds
	 * @return
	 */
	private BigInteger countSemiTables(final int nCols, final int colTotal, final int[] rowTotals) {
		final int nRows = rowTotals.length;		
		final int n1 = nRows/2;
		final int n2 = nRows - n1;
		int rowSum1 = 0;
		final int[] rowTotals1 = new int[n1];
		for(int i=0;i<n1;++i) {
			rowSum1 += rowTotals[i];
			rowTotals1[i] = rowTotals[i];
		}	
		final int[] rowTotals2 = new int[n2];
		for(int i=0;i<n2;++i) {
			rowTotals2[i] = rowTotals[n1+i];
		}
		final int targetSum = rowSum1;
		final OrderStepperTot stepper =  new OrderStepperTot(nCols,colTotal,targetSum);
		final IntFunc subF = new IntFunc() {
			@Override
			public BigInteger f(final int[] x) {
				final BigInteger xCount = countTablesSub(rowTotals1,x);
				if(xCount.compareTo(BigInteger.ZERO)>0) {
					final int[] y = new int[nCols];
					for(int i=0;i<nCols;++i) {
						y[i] = colTotal - x[i];
					}
					Arrays.sort(y);
					final BigInteger yCount = countTablesSub(rowTotals2,y);
					if(yCount.compareTo(BigInteger.ZERO)>0) {
						final BigInteger nperm = stepper.nPerm(x);
						return nperm.multiply(xCount).multiply(yCount);
					}
				}
				return BigInteger.ZERO;
			}
		};
		final Reducer summer = new SimpleSum();
		final BigInteger sum = summer.reduce(subF,stepper);
		return sum;
	}
	
	private BigInteger countTablesSub(final int[] rowTotalsIn, final int[] colTotalsIn) {
		// use as many symmetries as we can, right here
		int[] rowTotals = rowTotalsIn;
		int[] colTotals = colTotalsIn;
		Arrays.sort(rowTotals);
		Arrays.sort(colTotals);
		boolean swap = false;
		if(rowTotals.length!=colTotals.length) {
			swap = rowTotals.length>colTotals.length; 
		} else {
			swap = IntVec.compare(rowTotals, colTotals)>0; 
		}
		if(swap) {
			final int[] tmp = rowTotals;
			rowTotals = colTotals;
			colTotals = tmp;
		}
		// delegate problem
		final CPair counter = getSubCounter(rowTotals.length,colTotals.length);
		final int[] b = counter.prob.encodeB(rowTotals,colTotals);
		return counter.counter.countNonNegativeSolutions(b);
	}

	public BigInteger debugConfirmSqTables(final int rowsCols, final int total) {
		final int[] rows = new int[rowsCols];
		final int[] cols = new int[rowsCols];
		Arrays.fill(rows,total);
		Arrays.fill(cols,total);
		return countTablesSub(rows,cols);
	}
	
	public static void main(final String[] args) {
		System.out.println("n" + "\t" + "total" + "\t" + "count" + "\t" + "date" + "\t" + "cacheSizes");
		for(int n=1;n<=10;++n) {
			final CTab ctab = new CTab(10,true);
			for(int total=0;total<=(n*n-3*n+2)/2;++total) {
				final BigInteger count = ctab.countSqTables(n,total);
				final String cacheSizes = ctab.cacheSizesString();
				ctab.clearCaches();
				System.out.println("" + n + "\t" + total + "\t" + count + "\t" + new Date() + "\t" + cacheSizes);
			}
		}
		//System.out.println("total evals: " + SolnCache.totalEvals);
	}

}
