package com.mzlabs.fit;

import java.util.ArrayList;
import java.util.Arrays;

import cern.colt.matrix.DoubleMatrix1D;
import cern.colt.matrix.DoubleMatrix2D;
import cern.colt.matrix.impl.DenseDoubleMatrix1D;
import cern.colt.matrix.impl.DenseDoubleMatrix2D;
import cern.colt.matrix.linalg.Algebra;
import cern.colt.matrix.linalg.SingularValueDecomposition;

import com.winvector.linalg.LinalgFactory;
import com.winvector.linalg.colt.ColtMatrix;



public final class NewtonFitter implements Fitter {
	public final VectorFnWithJacobian fn;
	public ArrayList<Obs> obs = new ArrayList<Obs>();
	
	public NewtonFitter(final VectorFnWithJacobian fn) {
		this.fn = fn;
	}
	
	@Override
	public void clear() {
		obs = new ArrayList<Obs>();
	}
	
	@Override
	public void addObservation(final double[] x, final double y, final double wt) {
		if(!obs.isEmpty()) {
			final int n = obs.get(0).x.length;
			if(n!=x.length) {
				throw new IllegalArgumentException();
			}
		}
		final Obs obsi = new Obs(x,y,wt);
		obs.add(obsi);
	}
	
	public static String toString(final double[] x) {
		final StringBuilder b = new StringBuilder();
		b.append("{");
		boolean first = true;
		for(final double xi: x) {
			if(first) {
				first = false;
			} else {
				b.append(", ");
			}
			b.append(xi);
		}
		b.append("}");
		return b.toString();
	}
	
	/**
	 *  find zero of vecto function summed over data
	 *  via Newton's method over balance (should equal zero) and Jacobian
	 *  @return solution
	 */
	@Override
	public double[] solve() {
		final LinalgFactory<ColtMatrix> factory = ColtMatrix.factory;
		final int dim = fn.dim(obs.get(0));
		// roughly: often solving y ~ f(b.x), so start at f^-1(y) ~ b.x
		final Fitter sf = new LinearFitter(obs.get(0).x.length);
		for(final Obs obsi: obs) {
			sf.addObservation(obsi.x, fn.heuristicLink(obsi.y), obsi.wt);
		}
		double[] beta = sf.solve();
		if(beta.length!=dim) {
			beta = Arrays.copyOf(beta,dim);
		}
		final double[] balance = new double[dim];
		final ColtMatrix jacobian = factory.newMatrix(dim, dim, false);
		out:
		while(true) {
			fn.balanceAndJacobian(obs,beta,balance,jacobian);
			//System.out.println("Newston: beta=" + toString(beta) + ", balance=" + toString(balance));
			// add regularization of overall optimization terms f(beta) = dot(beta,beta) (balance and jacobian from gradient and hessian of f() as follows)
			final double epsilon = 1.0e-5;
			for(int i=0;i<dim;++i) {
				balance[i] += 2*epsilon*beta[i];
				jacobian.set(i,i,jacobian.get(i,i)+2*epsilon);
			}
			double absBalance = 0.0;
			for(final double gi: balance) {
				absBalance += Math.abs(gi);
			}
			if(Double.isInfinite(absBalance)||Double.isNaN(absBalance)||(absBalance<=1.0e-8)) {
				break out;
			}
			// neaten up system a touch before solving
			double totAbs = 0.0;
			for(int i=0;i<dim;++i) {
				for(int j=0;j<dim;++j) {
					totAbs += Math.abs(jacobian.get(i,j));
				}
			}
			if(Double.isInfinite(totAbs)||Double.isNaN(totAbs)||(totAbs<=1.0e-8)) {
				break out;
			}
			final double scale = (dim*dim)/totAbs;
			for(int i=0;i<dim;++i) {
				balance[i] *= scale;
				for(int j=0;j<dim;++j) {
					jacobian.set(i,j,jacobian.get(i,j)*scale);
				}
			}
			double[] delta = null;
			try {
				delta = jacobian.solve(balance);
			} catch (Exception ex) {
			}
			if(null==delta) {
				final DoubleMatrix2D jMat = new DenseDoubleMatrix2D(dim,dim);
				for(int i=0;i<dim;++i) {
					for(int j=0;j<dim;++j) {
						jMat.set(i,j,jacobian.get(i,j));
					}
				}
				final SingularValueDecomposition svd = new SingularValueDecomposition(jMat);
				final DoubleMatrix2D uMat = svd.getU();
				final DoubleMatrix2D sMat = svd.getS();
				final DoubleMatrix2D vMat = svd.getV();
				final Algebra algebra = Algebra.ZERO;
				// final DoubleMatrix2D recovered = algebra.mult(algebra.mult(uMat,sMat),algebra.transpose(vMat));
				for(int i=0;i<dim;++i) {
					final double sii = sMat.get(i,i);
					if(sii>0.01) {
						sMat.set(i,i,1/sii);
					} else {
						sMat.set(i,i,0.0);
					}
				}
				final DoubleMatrix1D bVec = new DenseDoubleMatrix1D(balance);
				final DoubleMatrix1D soln = algebra.mult(vMat,algebra.mult(sMat,algebra.mult(algebra.transpose(uMat),bVec)));
				// final DoubleMatrix1D check = algebra.mult(jMat,soln);
				delta = soln.toArray();
			}
			for(final double di: delta) {
				if(Double.isNaN(di)||Double.isNaN(di)) {
					break out;
				}
			}
			double deltaAbs = 0.0;
			for(int i=0;i<dim;++i) {
				beta[i] -= delta[i];
				deltaAbs += Math.abs(delta[i]);
			}
			if(deltaAbs<=1.0e-10) {
				break out;
			}
		}
		return beta;
	}

	@Override
	public double evalEst(final double[] beta, final double[] x) {
		return fn.evalEst(beta, x);
	}
}
