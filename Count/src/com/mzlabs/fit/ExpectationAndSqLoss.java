package com.mzlabs.fit;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Random;

import com.winvector.linalg.LinalgFactory;
import com.winvector.linalg.colt.ColtMatrix;

public final class ExpectationAndSqLoss implements VectorFnWithJacobian {
	public final Link link;
	
	public ExpectationAndSqLoss(final Link link) {
		this.link = link;
	}

	public static double dotNE(double[] beta, double[] x) {
		final int n = x.length;
		if(n+1!=beta.length) {
			throw new IllegalArgumentException();
		}
		double bx = 0.0;
		for(int i=0;i<n;++i) {
			bx += beta[i]*x[i];
		}
		return bx;
	}
	
	@Override
	public double evalEst(final double[] beta, final double[] x) {
		return link.invLink(dotNE(beta,x));
	}

	@Override
	public double heuristicLink(final double y) {
		return link.heuristicLink(y);
	}

	@Override
	public void balanceAndJacobian(final Iterable<Obs> obs, final double[] beta,
			final double[] balance, final ColtMatrix jacobian) {
		final int dim = beta.length;
		Arrays.fill(balance,0.0);
		for(int i=0;i<dim;++i) {
			for(int j=0;j<dim;++j) {
				jacobian.set(i,j,0.0);
			}
		}
		final double[] f = new double[3];
		for(final Obs obsi: obs) {
			final double lambda = beta[dim-1];
			final double bx = dotNE(beta,obsi.x);
			link.invLink(bx,f);
			{ // i,j < dim-1 case
				final double balCoef = obsi.wt*(2*f[0]-2*obsi.y+lambda)*f[1];
				final double jacCoef = obsi.wt*(2*f[1]*f[1] + (2*f[0]-2*obsi.y+lambda)*f[2]);
				for(int i=0;i<dim-1;++i) {
					final double xi = obsi.x[i];
					balance[i] += balCoef*xi;
					for(int j=0;j<dim-1;++j) {
						final double xj = obsi.x[j];
						final double jij = jacobian.get(i,j);
						jacobian.set(i,j,jij+xi*xj*jacCoef);
					}
				}
			}
			{ // i=dim-1, j<dim-1 case
				final int i = dim-1;
				balance[i] += obsi.wt*(f[0]-obsi.y);
				for(int j=0;j<dim-1;++j) {
					final double xj = obsi.x[j];
					final double jij = jacobian.get(i,j);
					jacobian.set(i,j,jij+obsi.wt*2*f[1]*xj);
				}
			}
			{ // i<dim-1, j=dim-1 case
				final int j = dim-1;
				for(int i=0;i<dim-1;++i) {
					final double xi = obsi.x[i];
					final double jij = jacobian.get(i,j);
					jacobian.set(i,j,jij+obsi.wt*f[1]*xi);
				}
			}
			// i==dim-1,j==dim-1 coef is zero
		}
	}

	@Override
	public int dim(final Obs obs) {
		return obs.x.length + 1;
	}
	
	@Override
	public String toString() {
		return "ExpectationAndSquareLoss(" + link + ")";
	}
	
	public static void main(final String[] args) {
		// build some example data
		final Random rand = new Random(343406L);
		final ArrayList<Obs> obs = new ArrayList<Obs>();
		for(int i=0;i<200;++i) {
			final double[] x = new double[] {1, rand.nextGaussian(), rand.nextGaussian()};
			final double yIdeal = Math.exp(x[0] + 2.0+x[1] + 3.0+x[2]);
			final double yObserved = Math.max(0.1,yIdeal + 0.4*rand.nextGaussian()*yIdeal);
			obs.add(new Obs(x,yObserved,1.0));
		}
		// provision fitters
		final ExpectationAndSqLoss fn = new ExpectationAndSqLoss(LinkBasedGradHess.logLink);
		final int elIndex = 2;
		final NewtonFitter[] fitters = { 
				new NewtonFitter(new SquareLossOfExp()),
				new NewtonFitter(DirectPoissonJacobian.poissonLink),
				new NewtonFitter(fn)  // elIndex == 2
		};
		final int dim = obs.get(0).x.length;
		final int nTrain = obs.size()/2;
		final LinearFitter lf = new LinearFitter(dim);
		// scan data
		for(int i=0;i<nTrain;++i) {
			final Obs obsi = obs.get(i);
			lf.addObservation(obsi.x,Math.log(obsi.y),1.0);
			for(final NewtonFitter fitter: fitters) {
				fitter.addObservation(obsi.x,obsi.y,1.0);
			}
		}
		// solve
		final double[] lfSoln = lf.solve();
		final double[][] fSoln = new double[fitters.length][];
		for(int j=0;j<fitters.length;++j) {
			fSoln[j] = fitters[j].solve();
		}
		// check balance condition
		final int pdim = fSoln[elIndex].length;
		final double[] balance = new double[pdim];
		final LinalgFactory<ColtMatrix> factory = ColtMatrix.factory;
		final ColtMatrix jacobian = factory.newMatrix(pdim,pdim,false);
		fn.balanceAndJacobian(obs.subList(0,nTrain), fSoln[elIndex], balance, jacobian);
		double balanceCheck = 0.0;
		for(int i=0;i<nTrain;++i) {
			final Obs obsi = obs.get(i);
			final double llfit = fn.evalEst(fSoln[elIndex],obsi.x);
			balanceCheck += obsi.wt*(obsi.y-llfit);
		}
		for(final double bi: balance) {
			if(Math.abs(bi)>1.0e-3) {
				throw new IllegalStateException("didn't balance");
			}
		}
		if(Math.abs(balanceCheck)>1.0e-3) {
			throw new IllegalStateException("didn't balance");
		}
		// print data and estimates
		for(int j=1;j<dim;++j) {
			System.out.print("x"+j + "\t");
		}
		System.out.print("y" + "\t" + "TestTrain" + "\t" + "logYest");
		for(int j=0;j<fitters.length;++j) {
			System.out.print("\t" + fitters[j].fn);
		}
		System.out.println();
		for(int i=0;i<obs.size();++i) {
			final Obs obsi = obs.get(i);
			for(int j=1;j<dim;++j) {
				System.out.print(obsi.x[j] + "\t");
			}
			System.out.print(obsi.y + "\t" + (i<nTrain?"train":"test") + "\t" + Math.exp(lf.evalEst(lfSoln,obsi.x)));
			for(int j=0;j<fitters.length;++j) {
				System.out.print("\t" + fitters[j].evalEst(fSoln[j],obsi.x));
			}
			System.out.println();
		}
		/**
		 R: steps
		 	
		 	library(ggplot2)
 			library(reshape2)
 			d <- read.table('expFit.tsv',sep='\t',stringsAsFactors=FALSE,header=TRUE)
 			ests <- c('logYest','SquareLossOfExp','GLM.PoissonRegression.log.link..','ExpectationAndSquareLoss.log.link.')
 			dTrain <- subset(d,TestTrain=='train')
 			dTest <- subset(d,TestTrain!='train')
 			# confirm poisson fit
			model <- glm(y~x1+x2,family=poisson(link='log'),data=dTrain)
			print(sum((dTrain[,'GLM.PoissonRegression.log.link..']-predict(model,type='response'))^2))
			# show balance and square error
 			for(v in ests) {
 			   print(paste(v,sum(dTrain$y-dTrain[,v]),sum((dTrain$y-dTrain[,v])^2)))
 			}
 			for(v in ests) {
 			   print(paste(v,sum(dTest$y-dTest[,v]),sum((dTest$y-dTest[,v])^2)))
 			}
			dplot <- melt(d,id.vars=c('x1','x2','TestTrain','y'),variable.name='estimateMethod',value.name='estimateValue')
			ggplot(data=dplot,aes(x=estimateValue,y=y,color=estimateMethod,shape=estimateMethod)) + 
			   geom_point() + geom_abline() + facet_wrap(~TestTrain,ncol=1)
			ggplot(data=dplot,aes(x=estimateValue,y=y,color=estimateMethod,shape=estimateMethod)) + 
			   geom_point() + geom_abline() + facet_wrap(~TestTrain,ncol=1) + scale_x_log10() + scale_y_log10()
			ggplot(data=subset(dplot,TestTrain!='train'),aes(x=estimateValue,y=y,color=estimateMethod,shape=estimateMethod)) + 
			   geom_point() + geom_abline() + facet_wrap(~estimateMethod) + guides(colour=FALSE,shape=FALSE)
			ggplot(data=subset(dplot,TestTrain!='train'),aes(x=estimateValue,y=y,color=estimateMethod,shape=estimateMethod)) + 
			   geom_point() + geom_abline() + facet_wrap(~estimateMethod) + scale_x_log10() + scale_y_log10() + guides(colour=FALSE,shape=FALSE)
			
		 */
	}
}
