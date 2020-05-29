/*********************************************
 * OPL 12.9.0.0 Model
 * Author: JIHU
 * Creation Date: 2020. 5. 26. at ¿ÀÈÄ 7:10:53
 *********************************************/

// problem size
 
int n = ...; //from datafile 
int cap = ...;
int numofveh = ...;
float v_avg = ...;

range P = 1..n;
range D = (n+1)..2*n;
range PU = 1..2*n;
range N = 0..(2*n +1);

// generate random data
tuple location {
	float x1;
	float y1; 
}
tuple edge {
	int i;
	int j;
}
setof(edge) edges = {<i,j> | i,j in N};
location node[N];
float nodex = ...;
float nodey = ...;
float t[edges];

int q[N];
int c[edges];

execute {
	function gettt(node1,node2){
		return (Opl.abs(node1.x1-node2.x1)+Opl.abs(node1.y1-node2.y1))/v_avg;	
	}
	for (var i in N) { 
		node[i].x1=nodex[i];
		node[i].y1=nodey[i];
	}	
	for (var e in edges) {
		t[e]=gettt(node[e.i],node[e.j])		
	}
}

// desicion variable
dvar boolean x[edges];
dvar int v[1..2*n];
dvar float Q[N];
dvar float B[N];

//expressions
dexpr float servedtrip = sum(e in edges) c[e]*x[e];

maximize servedtrip;

subject to{
	sum(j in N) x[<0,j>]==numofveh;
	sum(i in N) x[<i,2*n+1>]==numofveh;

	forall (j in PU)
	  flow_in:
	  sum(i in N) x[<i,j>] <= 1;
	  
	forall (i in PU)
	  flow_out:
	  sum(j in N) x[<i,j>] <= 1;
	 
	forall (i in PU)
	  flow:
	  (sum(j in N) x[<i,j>]) - (sum(j in N) x[<j,i>]) ==0;
	 
	forall (i in N, j in N)
	  timelimit1:
	  B[j] -B[i]+t[<i,j>] + 10000*(1-x[<i,j>]) >= 0;
	  
	forall (i in P)
	  timelimit2:
	  B[n+i] - B[i] - t[<i,n+i>] >= 0;

	forall (i in N, j in N)
	  caplimit1:
	  Q[j] - Q[i] - q[j] + 100*(1-x[<i,j>]) >= 0;
	
	forall (i in N)
	  caplimit2:
	  maxl(0,q[i]) - Q[i] <= 0;
	
	forall (i in N)
	  caplimit3:
	   minl(cap, cap+q[i]) - Q[i] >= 0;

	forall (i in N, j in N)
	  cvalue:
	  if (i in P && j in D){
	  	c[<i,j>]==1;
	  }
	  else {
	  	c[<i,j>]==0;	  
	  }
	
	forall (i in N)
	  qvalue:
	  if (i in P){
	  	q[i] ==1;
	  }
	  else if (i in D){
	  	q[i] ==-1;	  
	  }
	  else if (i == 0){
	  	q[i]==0;	  
	  }
	  else if (i == 2*n+1){
	  	q[i]==0;	  	  	  
	  }
	
	forall (j in PU)
	  vehlim1:
	  v[j] -j * x[<0,j>] >= 0;
	  
	forall (j in PU)
	  vehlim2:
	  v[j] - j * x[<0,j>] +n*(x[<0,j>]-1) <= 0;
	  
	forall (j in PU, i in PU)
	  vehlim3:
	  v[j] - v[i] -n*(x[<i,j>]-1)>= 0;
	  
	forall (j in PU, i in PU)
	  vehlim4:
	  v[j] - v[i]- n * (1-x[<i,j>]) <= 0;

}