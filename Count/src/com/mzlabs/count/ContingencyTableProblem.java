package com.mzlabs.count;

import java.util.Arrays;

public final class ContingencyTableProblem extends CountingProblem {
	private final int rows;
	private final int cols;

	/**
	 * 
	 * @param rows >0
	 * @param cols >0
	 * @return linear operator mapping contingency table interior to row totals and columns totals
	 */
	private static int[][] contingencyTable(final int rows, final int cols) {
		final int m = rows+cols;
		final int n = rows*cols;
		final int[][] A = new int[m][n];
		for(int i=0;i<rows;++i) {
			for(int j=0;j<cols;++j) {
				final int cell = i*cols+j;
				A[i][cell] = 1;
				A[j+rows][cell] = 1;
			}
		}
		return A;
	}

	/**
	 * 
	 * @param rows >0
	 * @param cols >0
	 */
	public ContingencyTableProblem(final int rows, final int cols) {
		super(contingencyTable(rows,cols));
		this.rows = rows;
		this.cols = cols;
	}
	
	@Override
	public int[] normalForm(int[] b) {
		final int[] bsort = Arrays.copyOf(b,b.length);
		Arrays.sort(bsort,0,rows);
		Arrays.sort(bsort,rows,rows+cols);
		return bsort;
	}

}
