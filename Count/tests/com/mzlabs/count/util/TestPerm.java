package com.mzlabs.count.util;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

import com.mzlabs.count.ContingencyTableProblem;

public class TestPerm {
	
	@Test 
	public void testSort() {
		final int[] values = new int[3];
		do {
			final Permutation p = Permutation.sortingPerm(values, 0, values.length,values.length);
			final int[] sorted = p.apply(values);
			for(int i=1;i<values.length;++i) {
				assertTrue(sorted[i-1]<=sorted[i]);
			}
		} while(IntVec.advanceLT(2,values));
	}
	
	@Test
	public void sortBug() {
		final ContingencyTableProblem problem = new ContingencyTableProblem(3,2);
		final int[] b = {1,0,0,0,1};
		final Permutation p = problem.toNormalForm(b);
		final int[] sorted = p.apply(b);
		for(int i=1;i<problem.rows;++i) {
			assertTrue(sorted[i-1]<=sorted[i]);
		}
		for(int i=1+problem.rows;i<problem.rows+problem.cols;++i) {
			assertTrue(sorted[i-1]<=sorted[i]);
		}
	}
	
	@Test
	public void testComp2() {
		//  Herstein circle notation (T o P)(x) = P(T(x)) (p. 13, Topics in Algebra 2nd edition)
		final Permutation T = Permutation.newPerm(new int[] {2, 0, 1, 3, 4});
		final Permutation P = Permutation.newPerm(new int[] {0, 1, 2, 3, 4});
		final int[] x = {1,0,0,0,1};
		final Permutation comp = T.compose(P);
		final int[] map = comp.apply(x);
		assertNotNull(map);
		assertEquals(x.length,map.length);
		final int[] check = P.apply(T.apply(x));
		assertNotNull(check);
		assertEquals(x.length,check.length);
		for(int i=0;i<check.length;++i) {
			assertEquals(check[i],map[i]);
		}
	}
	
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
		//  Herstein circle notation (T o P)(x) = P(T(x)) (p. 13, Topics in Algebra 2nd edition)
		final Permutation T = Permutation.newPerm(new int[] {1, 0, 2});
		final Permutation P = Permutation.newPerm(new int[] {0, 2, 1});
		final int[] x = { 0, 1, 2};
		final Permutation comp = T.compose(P);
		final Permutation other = P.compose(T);
		assertTrue(comp.compareTo(other)!=0); // check our test is strong enough to check the effect we want
		final int[] map = comp.apply(x);
		assertNotNull(map);
		assertEquals(x.length,map.length);
		final int[] check = P.apply(T.apply(x));
		assertNotNull(check);
		assertEquals(x.length,check.length);
		for(int i=0;i<check.length;++i) {
			assertEquals(check[i],map[i]);
		}
	}

}
