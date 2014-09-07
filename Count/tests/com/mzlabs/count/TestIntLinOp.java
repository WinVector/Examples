package com.mzlabs.count;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

import com.mzlabs.count.util.IntLinOp;

public class TestIntLinOp {
	@Test
	public void testFn() {
		final int[][] A = { {1, 1, 0}, {0, 0, 1}, {1, -4, 2}, {0,0,0} };
		final int[] x = {1,5,-2};
		final int[] check = new int[A.length];
		IntLinOp.mult(A, x, check);
		final int[] res = new int[A.length];
		new IntLinOp(A).mult(x, res);
		for(int i=0;i<check.length;++i) {
			assertEquals(check[i],res[i]);
		}
	}
}
