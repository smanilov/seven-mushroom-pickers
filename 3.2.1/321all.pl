# this is a prototype of 3.2.1 all subtasks which extracts data which is fed as features to an ML/causal model. 
# Add confidence intervals or correctness probability (esp with fuzzy)
@files=<*.html>;
#print @files;
$fcount=0;
$allfiles=scalar(@files);
foreach $file (@files){
	$fcount++;
	if($fcount>20) { print "FILES $fcount\n"; exit;}
	%classes=();
	%itemprops=();
	if($fcount%10==0) { print "$fcount\n";}
	open FI,"<$file" or die "Cannot read $file";
	$topCcnt=0;
	$topCname="~NASO";
	$topIcnt=0;
	$topIname="~NASO";
	$gtmcount=0;
	$extcsscount=0;
	while(<FI>){
		if(/link(.+)css/){
			#print "$_ $1\n";
			$extcsscount++;
		}
		if(/class\s*=\s*\"([^"]+)\"/){
			$classname=$1; 
			if(!defined($classes{$classname})) { $classes{$classname}=0; }
			$classes{$classname}++;
			if($classes{$classname}>$topCcnt){
				$topCcnt=$classes{$classname};
				$topCname=$classname;
			}
		}
		if(/googletagmanager/){$gtmcount++;}
		if(/itemprop\s*=\s*\"([^"]+)\"/){
			$classname=$1; 
			if(!defined($itemprops{$classname})) { $itemprops{$classname}=0; }
			$itemprops{$classname}++;
			if($itemprops{$classname}>$topIcnt){
				$topIcnt=$itemprops{$classname};
				$topIname=$classname;
			}
		}
		
	}
	print "$file $extcsscount $gtmcount $topCcnt $topIcnt $topCname $topIname\n";
	close FI;
}