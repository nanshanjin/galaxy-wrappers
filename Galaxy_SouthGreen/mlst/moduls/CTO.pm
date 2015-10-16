package CTO;#Create Tree and Out

use strict;
use Exporter;
use Bio::Tree::DistanceFactory;
use Bio::Matrix::IO;
use Bio::TreeIO;
use Bio::Tree::Draw::Cladogram;

our @ISA= qw( Exporter );

# these CAN be exported.
our @EXPORT_OK = qw( calcTree drawTree );

# these are exported by default.
our @EXPORT = qw( calcTree );

=for comment

	FILE		CTO.pm - for calculate and create trees (3rd step)
	AUTHOR 		Verdier Axel
	CREATE_DATE	04-25-2014 (mm-dd-yyyy)
	LAST_DATE	05-26-2014
	FUNCTIONS	calcTree
			calcTree - generate a tree with a distance matrix and return it
=cut

#FUNCTIONS
#====================
=head1 calcTree

	Overview	generate a tree with a distance matrix and return it
	
	parameters	0:matrixDist 1:matrixName
			matrixDist: The types distances matrix
			param2:The matrix of the name of the types
			
	return		Bio::Tree::Tree
	
	example		my $tree=CTO::calcTree(\@matrixDist, \@nameTypes, $inTypeId);
=cut
sub calcTree{
	my @matrixDist=@{@_[0]};
	my @matrixName=@{@_[1]};
	my $inTypeId=@_[2];
	my $separator = "\t";
	
	if (@matrixDist != @matrixName){
		print "\nERROR : in CTO.pm\n\t=> generate tree : unegale matrix !\n\tPlease report it\n";
		exit 1;
	}
	
	my $file_content=" ".@matrixName."\n";
	
	for(my $i=0; $i<@matrixName; $i++){
		$file_content.=$matrixName[$i];
		for (my $j=0; $j<@matrixName; $j++){
			$file_content.=$separator.($matrixDist[$i][$j]);
		}
		$file_content.="\n";
		
	}
	
	my $treeMake = Bio::Tree::DistanceFactory->new(-method => 'NJ');
	my $treeout = Bio::TreeIO->new(-format => 'newick');
	
	my $parser = Bio::Matrix::IO->new(	-format => 'phylip',
						-string => $file_content);
	my $mat=$parser->next_matrix();
	my $tree=$treeMake->make_tree($mat);
	
	#change color of the node
	my ($node) = $tree->find_node( -id => $matrixName[$inTypeId]);
	$node->add_tag_value('Rcolor', 1);
	$node->add_tag_value('Gcolor', 0);
	$node->add_tag_value('Bcolor', 0);
	return $tree;
}	
1;


