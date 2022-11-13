# this is a prototype of 3.1.2 all subtasks 
@files=<*.html>;
#print @files;
$fcount=0;
$allfiles=scalar(@files);

$cnt=0;
%nsr=();
open FI,"<batch_whois.csv";
$_=<FI>; #header
while(<FI>){
	$cnt++;
	chomp;
	@fields=split/,/;
	$fcnt=scalar(@fields);
	#if($fcnt!=10) { print "ERROR $fcnt $fields[0] \n"; next; }
	$nsr{$fields[0]}=$fields[1];
	print "$fields[0] $fields[1]\n";
}

print $nsr{"100percentfedup.com"};
print "\n";
foreach $file (@files){
	if($file =~ /^(.*)\.html/){
		$website= $1;
		$prov=$nsr{$website};
		if(!defined($nsr{$website})){ $prov=""; }
		print "$website $prov\n";
	}
}