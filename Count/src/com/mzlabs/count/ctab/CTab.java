package com.mzlabs.count.ctab;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.util.IntVec;
import com.mzlabs.count.zeroone.ZeroOneCounter;


public final class CTab {
	
	private static final class CPair {
		public ContingencyTableProblem prob = null;
		public NonNegativeIntegralCounter counter = null;
	}
	
	private final Map<IntVec,CPair> counters = new  HashMap<IntVec,CPair>();

	
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
		final OrderStepper stepper = new OrderStepper(rowsCols,total);
		BigInteger sum = BigInteger.ZERO;
		final int[] x = new int[rowsCols];
		final int[] y = new int[rowsCols];
		final int n1 = rowsCols/2;
		final int n2 = rowsCols - n1;
		final int targetSum = n1*total;
		do {
			int xsum = 0;
			for(final int xi: x) {
				xsum += xi;
			}
			if(targetSum==xsum) {
				final BigInteger xCount = countSemiTables(n1,total,x);
				final BigInteger nperm = stepper.nPerm(x);
				for(int i=0;i<rowsCols;++i) {
					y[i] = total - x[i];
				}
				Arrays.sort(y);
				final BigInteger yCount = countSemiTables(n2,total,y);
				sum = sum.add(nperm.multiply(xCount).multiply(yCount));
			}
		} while(stepper.advanceLEI(x));
		return sum;
	}
	
	private CPair getSubCounter(final int nRows, final int nCols) {
		final IntVec counterKey = new IntVec(new int[] { nRows, nCols});
		CPair counter = null;
		synchronized (counters) { // essentially serialized here
			counter = counters.get(counterKey);
			if(null==counter) {
				final ContingencyTableProblem cp = new ContingencyTableProblem(nRows,nCols);
				counter = new CPair();
				counter.prob = cp;
				counter.counter = new ZeroOneCounter(cp,false);
				counters.put(counterKey,counter);
			}
		}
		return counter;
	}

	/**
	 * count number of contingency table fill-ins with nCols (all summing to colBound) and rows summing to rowBounds 
	 * @param nCols >0
	 * @param colBound >0
	 * @param rowBounds
	 * @return
	 */
	private BigInteger countSemiTables(final int nCols, final int colBound, final int[] rowTotals) {
		// TODO: split one more time before going to base-case counter
		final int nRows = rowTotals.length;
		final int[] colTotals = new int[nCols];
		Arrays.fill(colTotals,colBound);
		final CPair counter = getSubCounter(nRows,nCols);
		final int[] b = counter.prob.encodeB(rowTotals,colTotals);
		return counter.counter.countNonNegativeSolutions(b);
	}
	
	public BigInteger debugConfirmSqTables(final int rowsCols, final int total) {
		final CPair counter = getSubCounter(rowsCols,rowsCols);
		final int[] b = new int[2*rowsCols];
		Arrays.fill(b,total);
		return counter.counter.countNonNegativeSolutions(b);
	}
	
	public static void main(String[] args) {
		final CTab ctab = new CTab();
		for(int rowsCols=1;rowsCols<=4;++rowsCols) {
			for(int total=0;total<=10;++total) {
				final BigInteger count = ctab.countSqTables(rowsCols,total); 
				final BigInteger check = ctab.debugConfirmSqTables(rowsCols, total);
				final boolean eq = (check.compareTo(count)==0);
				System.out.println(rowsCols + "\t" + total + "\t" + count + "\t" + check + "\t" + eq);
			}
		}
	}
}
