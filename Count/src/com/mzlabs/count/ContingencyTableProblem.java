package com.mzlabs.count;

import java.util.Arrays;

import com.mzlabs.count.perm.Permutation;

public final class ContingencyTableProblem extends CountingProblem {
	private final int rows;
	private final int cols;
	

	private static int[] coords(final int rows, final int cols, final int index) {
		final int coords[] = new int[2];
		coords[0] = index%cols;
		coords[1] = (index - coords[0])/cols;
		return coords;
	}
	
	private int[] coords(final int index) {
		return coords(rows,cols,index);
	}
	
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
				final int[] coords = coords(rows,cols,cell);
				if((j!=coords[0])||(i!=coords[1])) {
					throw new IllegalStateException("coords are wrong");
				}
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
	public boolean admissableB(final int[] b) {
		if(b.length!=rows+cols) {
			return false;
		}
		for(final int bi: b) {
			if(bi<0) {
				return false;
			}
		}
		int sum1 = 0;
		for(int i=0;i<rows;++i) {
			sum1 += b[i];
		}
		int sum2 = 0;
		for(int i=rows;i<rows+cols;++i) {
			sum2 += b[i];
		}
		if(sum1!=sum2) {
			return false;
		}
		return true;
	}
	
	@Override
	public Permutation toNormalForm(final int[] b) {
		final int n = b.length;
		final Permutation p1 = Permutation.sortingPerm(b, 0, rows, n);
		final Permutation p2 = Permutation.sortingPerm(b, rows, rows+cols, n);
		return p1.compose(p2); // disjoint indices in perms, so doesn't matter which order we compose
	}
	
	@Override
	public int[][] splitVarsByRef(final int[] curVarSet) {
		final int nVar = curVarSet.length;
		if(nVar<=1) {
			throw new IllegalArgumentException("called on unsplittable set");
		}
		final int nCoords = 2;
		final double[] min = new double[nCoords];
		Arrays.fill(min,Double.POSITIVE_INFINITY);
		final double[] max = new double[nCoords];
		Arrays.fill(max,Double.NEGATIVE_INFINITY);
		final double[] sum = new double[min.length];
		for(final int idx: curVarSet) {
			final int[] coords = coords(idx);
			for(int jj=0;jj<nCoords;++jj) {
				min[jj] = Math.min(min[jj],coords[jj]);
				max[jj] = Math.max(max[jj],coords[jj]);
				sum[jj] += coords[jj];
			}
		}
		int widestJ = 0;
		for(int j=1;j<nCoords;++j) {
			if((max[j]-min[j])>(max[widestJ]-min[widestJ])) {
				widestJ = j;
			}
		}
		final double mean = sum[widestJ]/(double)nVar;
		final boolean[] left = new boolean[nVar];
		int nLeft = 0;
		for(int i=0;i<nVar;++i) {
			final int[] coords = coords(curVarSet[i]);
			if(coords[widestJ]<mean) {
				left[i] = true;  // store in a boolean to work around floating point non-determinism
				++nLeft;
			}
		}
		final int[][] split = new int[2][];
		if((nLeft<=0)||(nLeft>=nVar)) {
			throw new IllegalStateException("failed to split");
		}
		split[0] = new int[nLeft];
		split[1] = new int[nVar-nLeft];
		nLeft = 0;
		int nRight = 0;
		for(int i=0;i<nVar;++i) {
			if(left[i]) {
				split[0][nLeft] = i;
				++nLeft;
			} else {
				split[1][nRight] = i;
				++nRight;
			}
		}
		return split;
	}

}
