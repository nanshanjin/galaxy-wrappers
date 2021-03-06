#!/usr/bin/perl
 
use Getopt::Long;
use lib;
use Pod::Usage; 
use Net::SCP;
use JSON;
binmode STDOUT, ":utf8";
use utf8;
#  
use File::Temp qw/ tempfile tempdir /;
 
my $vcffile; 
my $tool_directory; 
my $help; 
my $tbi;
my $bgzip; 
my $output_tbi;
my $html;
my $host = "salanque.cirad.fr";
my $user = "galaxy";
my $json = "template.json";

my $scp = Net::SCP->new($host);
$scp->login($user); 
GetOptions(
    'vcffile=s'       => \$vcffile, 
    'tool_directory=s'=> \$tool_directory,  
    'html=s'          => \$html, 
    'help|h|?'        => \$help
) ;
my $file_vcf = $tool_directory ."/galaxy$$.vcf";
#my $tabix_cmd = "source " . $tool_directory. "/module_vcf2jbrowse.sh; bgzip ". $vcffile ."; tabix -p vcf ". $vcffile .".gz";


my $tabix_cmd = "source " . $tool_directory. "/module_vcf2jbrowse.sh; cp ". $vcffile ." " . $file_vcf ."; bgzip ". $file_vcf ." ; tabix -p vcf ". $file_vcf .".gz";
system("scp ". $user ."@". $host.":/opt/projects/jbrowse.southgreen.fr/prod/databases/oryza_sativa_japonica_v7/trackList.json " . $tool_directory."/trackList.json");
my $output = `grep -v "#" $vcffile | sed -n '1p' | cut -f 1,2 `;
chomp($output);
my ($chr,$start) = (split(/\t/,$output))[0,1];
my $end = $start + 500000;
my $location = $chr."%3A".$start."..".$end; 
my $json;
{
    local $/; #Enable 'slurp' mode
    open my $fh, "<", $tool_directory."/trackList.json";
    $json = <$fh>;
    close $fh;
}
my $data = decode_json($json);

system("sed  s:FILE:tmp/galaxy$$.vcf.gz:g ".$tool_directory."/template.json > ".$tool_directory."/galaxy$$.json"); 

push @{$data->{'include'}} , "galaxy$$.json";
open my $fh, ">".$tool_directory."/trackList.json";
print $fh to_json($data,{ utf8 => 1, pretty => 1 });
close $fh;
system($tabix_cmd);
my $file_gz = "galaxy$$.vcf.gz";
my $file_tbi = "galaxy$$.vcf.gz.tbi";

system("scp ". $file_vcf.".gz.tbi ". $user ."@". $host.":/opt/projects/jbrowse.southgreen.fr/prod/databases/oryza_sativa_japonica_v7/tmp/" .$file_tbi); 
system("scp ". $file_vcf.".gz ". $user ."@". $host.":/opt/projects/jbrowse.southgreen.fr/prod/databases/oryza_sativa_japonica_v7/tmp/". $file_gz);
system("scp ".$tool_directory."/galaxy$$.json ". $user ."@". $host.":/opt/projects/jbrowse.southgreen.fr/prod/databases/oryza_sativa_japonica_v7/");
system("scp ".$tool_directory."/trackList.json ". $user ."@". $host.":/opt/projects/jbrowse.southgreen.fr/prod/databases/oryza_sativa_japonica_v7/trackList.json");
system("rm  ".$tool_directory."/trackList.json ".$tool_directory."/galaxy$$.json ".$file_vcf.".gz ".$file_vcf.".gz.tbi ");

open(HTML,">$html");
print HTML "<html><body><div><a href='http://jbrowse.southgreen.fr/?data=oryza_sativa_japonica_v7&loc=".$location."&tracks=DNA%2CMSUGeneModels%2Ctmp%2fgalaxy$$.vcf.gz&highlight=' target='_blank'>View on Jbrowse</a></div></body></html>";
close HTML;

