package com.mzlabs.count.perm;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class TestPerm {
	
	@Test
	public void testPerm() {
		final int[] values = {1, 5, 2, 2, 7, -4};
		final Permutation p = Permutation.sortingPerm(values,0,values.length,values.length);
		//System.out.println(p);
		final int[] sorted = p.apply(values);
		assertNotNull(sorted);
		assertEquals(values.length,sorted.length);
		for(int i=1;i<sorted.length;++i) {
			assertTrue(sorted[i-1]<=sorted[i]);
		}
		final int[] orig = p.applyInv(sorted);
		assertNotNull(orig);
		assertEquals(values.length,orig.length);
		for(int i=0;i<orig.length;++i) {
			assertEquals(values[i],orig[i]);
		}
		//System.out.println("break");
	}
	
	
	@Test
	public void testSubRangePerm() {
		final int[] values = {1, 5, 2, -2, 7, -4};
		final Permutation p = Permutation.sortingPerm(values,1,4,values.length);
		final int[] sortedRange = p.apply(values);
		assertNotNull(sortedRange);
		assertEquals(values.length,sortedRange.length);
		final int[] expect = {1, -2, 2, 5, 7, -4};
		for(int i=0;i<values.length;++i) {
			assertEquals(expect[i],sortedRange[i]);
		}
	}
	
	@Test
	public void testComp() {
		final Permutation p1 = new Permutation(new int[] {1, 0, 2});
		final Permutation p2 = new Permutation(new int[] {0, 2, 1});
		final int[] x = { 0, 1, 2};
		final Permutation comp = p1.compose(p2);
		final int[] map = comp.apply(x);
		assertNotNull(map);
		assertEquals(x.length,map.length);
		final int[] check = p1.apply(p2.apply(x));
		assertNotNull(check);
		assertEquals(x.length,check.length);
		for(int i=0;i<check.length;++i) {
			assertEquals(check[i],map[i]);
		}
	}

}
