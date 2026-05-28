#!perl

use strict;
use Getopt::Long;
use MaterialsScript qw(:all);
use List::Util qw(shuffle max);
use constant TRUE 	=> 1;
use constant FALSE 	=> 0;
use constant DEBUG	=> 1; # larger is more verbose
use constant PICO_TO_FEMTO => 1000; #ps*1000=>fs,


# Purpose: 	Crosslink oligomers and curing agents using atomistic models
# Modules:	Materials Visualizer, Forcite, COMPASS
# Last revised:	Dec 19, 2013

# Creates cross links in a system containing a oligomers and crosslinking molecules.
# Atoms on the oligomers and crosslinkers are designated as reactive atoms by assigning 
# a special name to the atoms (usually R1 and R2). Close-contacts are calculated between 
# the reactive atoms and bonds are created. The close-contact distance is increased
# when no progress is made.

# Executes these steps:
#   1. One-time equilibration with NVT and then NPT dynamics
#   2. Update reaction radius
#   3. Create new crosslinks (createNewXlinks)
#   4. Relax with optimization and dynamics
#   5. Open epoxy rings (optional)
#   6. Delete condensates (optional)
#   7. Adjust hydrogens
#   8. Recalculate charge groups (optional)
#   9. Anneal xlinked structure using temperature cycle (optional)
#  10. Write xlink data to study tables
#  11. Repeat steps 2-10 until target conversion or max cutoff is reached
#  12. Delete excess xlinks if conversion exceeds target

# Input documents:

# (1) A periodic atomistic xsd file containing a mixture of oligomers and xlinkers with
#     their reactive atoms labeled (usually as R1 and R2 respectively).

# Output documents:

# (1) xlink_final.xsd - Final xlinked structure 
# (2) xlink_statistics.std - Table of xlinking and thermo data
# (3) xlink_structures.std - Table of intermediate structures at lower conversion levels
# (4) XlinkBonds.xcd - Distribution of bond lengths to check for stretched bonds
# (5) Progress.txt - Log file updated continuously during the run
# (6) Timings.txt - Log file of cpu time

# Limitations:
#
# * No ring spearing check (but keep an eye on max bond energy)
# * Need to have at least two atoms in the xlinker
# * Tracks but does not reject intramolecular bonds - these can be formed

# Change log
#
# JW 07/20/2011 Restraint method (optional) for smoother crosslinking
# JD 12/27/2012 Tcycle optional, error trapping, automatic charge groups, improve xlink stats
# JD 01/30/2013 Max bond energy, graceful fault on relaxNPT
# JD 02/11/2013 Redesigned user inputs for use from the User menu via GUI
# JD 02/28/2013 Support restarts on partially xlinked systems
# JD 03/04/2013 Fixed bug in T, P statistics
# JD 03/07/2013 Optional turn off maxbond, skip straightdynamicsNPT for first radius
# JD 03/20/2013 Geometry optimize after each restraint tightening - helps avoid crashes
# JD 10/03/2013 $remove_condensation option, eliminate molecule name requirements
# JD 12/04/2013 Fix bug that occasionally produces multiple xlinks on a single reactive atom
# JD 12/12/2013 Option for atoms to react multiple times
# JD 12/16/2013 Improve maxbond performance
# JD 12/19/2013 Remove clutter by using one dynamics subroutine
 
################################################################################################
#
# Begin user settings
#
################################################################################################

my $xsdDoc				= Documents->ActiveDocument;
#my $xsdDoc				= $Documents{"24_12_2.xsd"};

# Get the user supplied options
my %Arg;
GetOptions(\%Arg,
	"Forcefield=s", 
	"Conversion=i", 
	"MinRxnRadius=f", 
	"MaxRxnRadius=f", 
	"StepRxnRadius=f",
	"Iterations_per_Radius=i", 
	"ChargeMethod=s", 
	"Temperature=f",
	"TemperatureCycle=s",
	"Initial_Equil_ps=f",
	"OpenRings=s",
	"Condensation=s",
	"React_Multi_Oligomer=s",
	"React_Multi_Xlinker=s"
);

my $conversionTarget 			= $Arg{Conversion};
my $MinRxnRadius 			= $Arg{MinRxnRadius};
my $StepRxnRadius 			= $Arg{StepRxnRadius};
my $MaxRxnRadius 			= $Arg{MaxRxnRadius};
my $IterationsPerRadius			= $Arg{Iterations_per_Radius};
#my $IterationsPerRadius			= 5;

#my $conversionTarget 			= 100;	# Percent of reactive atoms on oligomer that react
#my $MinRxnRadius 			= 3.0;	# Initial close contacts cutoff
#my $StepRxnRadius 			= 1.0;	# Close contact step size
#my $MaxRxnRadius 			= 13.0;	# Final close contacts cutoff - hopefully conversion
						# is reached before this value is reached
						
# Atom and molecule details - need to be set in the input document!

my $oligomerName 			= "oligomer";	# Oligomer molecules are all given this name to help track stats
my $oligomerReactiveAtom 		= "R1";		# The name of the reactive atom(s) in the oligomer molecule

# Ring opening set on oligomer - if you don't want ring opening, set $openRing to "N" and ignore
my $openRing				= FALSE;
$openRing				= TRUE  if ($Arg{OpenRings} eq "Yes");
my $deleteAtom 				= "O";		# Delete bond between R1 and this atom - for ring opening

# Condensation: Remove OH group from reacted atoms?
my $remove_condensation			= FALSE;
$remove_condensation			= TRUE  if ($Arg{Condensation} eq "Yes");

# Allow multiple reactions?
my $react_multi_oligomer		= FALSE;
$react_multi_oligomer			= TRUE  if ($Arg{React_Multi_Oligomer} eq "Yes");
my $react_multi_xlinker			= FALSE;
$react_multi_xlinker			= TRUE  if ($Arg{React_Multi_Xlinker} eq "Yes");

my $xlinkerName 			= "xlinker";	# Xlinker molecules are all given this name to help track stats
my $xlinkerReactiveAtom 		= "R2";		# The name of the reactive atom(s) in the cross linking molecule

# Simulation settings

my $forcefield		 	= $Arg{Forcefield};
#my $forcefield		 	= "COMPASS";
my $timeStep			= 1;			# Dynamics time step in fs
my $chargeMethod 		= $Arg{ChargeMethod};	# Atom based, Group based, Ewald
#my $chargeMethod 		= "Ewald";
my $Quality			= "Fine";		# Coarse/Medium/Fine/Ultra Fine
my $thermostat			= "Andersen";		# Andersen, Nose, Velocity Scale, or Berendsen
my $xlinkTemperature		= $Arg{Temperature};	# Main temperature throughout
#my $xlinkTemperature		= 300;
my $xlinkPressure		= 0.0001;		# Main pressure throughout

my $one_time_equilibration	= $Arg{Initial_Equil_ps};	# ps
#my $one_time_equilibration	= 50.0;	# ps

# Options for the perturbations -  Temperature cycle settings
my $startTemp				= $xlinkTemperature;			# Starting temperature
my $lowTemp				= $xlinkTemperature;			# Ending temperature
my $UseTempCycle			= FALSE;
$UseTempCycle				= TRUE  if ($Arg{TemperatureCycle} eq "Yes");
#my $UseTempCycle			= FALSE;	# turn temperature cycle on/off
my $highTemp				= $xlinkTemperature + 300;	# High temperature
my $tempStep				= 20;		# Temperature increment in degrees K
my $tempDuration			= 20.0;		# Time at each temperature (ps)

# Analysis NPT settings
my $analyzeDuration			= 5.0;		# ps of NPT dynamics for sampling thermo data

# NPT dynamics before crosslinking at each new distance
my $straightDynamicsTime		= 50.0;		# Time in ps

# Parameters for temporary restraint bonds used to bring Xlinked bonds together smoothly
my $UseRestraintBonds			= TRUE;		# turn smoothing algorithm on/off
my $RestraintBondingTargetLength 	= 1.47;		# use C-N bond parameters from CVFF
my $RestraintForceConstant 		= 356.5988;
my $nRestraintBondingStages		= 5;		# increments for smoothly increasing restraint bonds
my $relax_length 			= 10;		# time (ps) to relax structures before bonding

# Option for calculating the largest bond energy to help assess network strain and possible ring spearing
# Could impact performance, but algorithm has been tuned to speed it up
my $UseMaxBondEnergy			= TRUE;

# Option for deleting any extra xlink bonds if we overshoot the target conversion
my $deleteExcessXlinks			= TRUE;

###########################################################################################
#
# End user settings
#
###########################################################################################

# Import some server files with info on hostname, mpi, arguments
eval 
{
	Documents->Import("fromdsd.txt");
	Documents->Import("mpd.hosts");
};

# File for reporting run progress
my $textDoc = Documents->New("Progress.txt");

# Start by writing options specified by user in the GUI
$textDoc->Append("USER OPTIONS\n============================\n");
while ( my ($key, $value) = each(%Arg) ) 
{
	$textDoc->Append(sprintf "$key => $value\n");
}
$textDoc->Append("============================\n\n");

# File for reporting time taken by each cycle 
my $timeDoc = Documents->New("Timings.txt");
$timeDoc->Append("Distance, Iteration, Elapsted_Time(hr), Segment_Time(hr), Conversion(%)\n");
my $segtime = time; # Time in seconds for a segment of the run

# Initialise Forcite with settings to be used globally
my $Forcite = Modules->Forcite;
$Forcite->ChangeSettings([	
	CurrentForcefield		=> $forcefield,
	Quality				=> $Quality,
	'3DPeriodicElectrostaticSummationMethod' => $chargeMethod,
	'3DPeriodicvdWSummationMethod' 	=> "Atom based",
	"Use3DPeriodicElectrostaticEwaldLookupTable"     => "Yes",
	"Use3DPeriodicvdWAtomLongRangeCorrection"        => "Yes",
	"3DPeriodicElectrostaticEwaldSumAccuracy"        => 1e-004, 
	"3DPeriodicvdWAtomCubicSplineCutOff"             => 18.5,
	"3DPeriodicvdWEwaldSumAccuracy"                  => 1e-005,
	"3DPeriodicElectrostaticPPPMAccuracy"            => 1e-005, 
	AssignChargeGroups			         => "No",
	ChargeGroupAssignmentMethod                      => "Divide-and-conquer",
	TotalChargeTolerance                             =>  0.01,  
	Temperature			=> $xlinkTemperature,
	Pressure			=> $xlinkPressure,
	Thermostat			=> $thermostat,
	Barostat			=> "Andersen",
	TimeStep			=> $timeStep,
	TrajectoryFrequency		=> 5000,
	AppendTrajectory		=> "No",
	WriteVelocities			=> "Yes",
	EnergyDeviation			=> 1000000000000,
	WriteLevel			=> "Silent"
]);

# Make a copy of the first document to preserve the starting structure
my $rootName = "xlink";
my $doc = Documents->New("$rootName.xsd");
$doc->CopyFrom($xsdDoc);

# Prevent filename conflict for restart runs
$xsdDoc->Name = "initial" if ($xsdDoc->Name eq "xlink_final");
$xsdDoc->Close;

# Create a study table to hold the statistics
my $statTable = Documents->New($rootName."_statistics.std");
my $nstatsheets = 1;

# Create a study table to hold the intermediate structures at the end of each distance cycle
# This can be used for further analysis of the evolution of the system.
# (could be merged with the above, but would have to shift the columns to the right)
my $structureTable = Documents->New($rootName."_structures.std");
$structureTable->ColumnHeading(1) = "Distance (A)";
$structureTable->ColumnHeading(2) = "Iteration";
$structureTable->ColumnHeading(3) = "Percent Conversion";



###########################################################################################
# Initialize the crosslinking stuff

# Count the reacted and reactive atoms
my $reactiveOligomerAtoms = 0;
my $reactiveXLinkerAtoms  = 0;
my $reactedOligomerAtoms  = 0;
my $reactedXLinkerAtoms   = 0;
my $totalOligomerAtoms    = 0;
foreach my $atom (@{$doc->UnitCell->Atoms})
{
	$reactiveOligomerAtoms++ if ( isReactiveR1($atom) );
	$reactiveXLinkerAtoms++  if ( isReactiveR2($atom) );
	$reactedOligomerAtoms++  if ($atom->Name =~ /^$oligomerReactiveAtom-\d/);
	$reactedXLinkerAtoms++   if ($atom->Name =~ /^$xlinkerReactiveAtom-\d/);
	$totalOligomerAtoms++    if ($atom->Name =~ /^$oligomerReactiveAtom/);
}

# xlinkPotential is the number of possible crosslinks that the xlinkers can form
my $xlinkPotential = $reactiveXLinkerAtoms;
if ($react_multi_xlinker)
{
	$xlinkPotential = 0;
	foreach my $atom (@{$doc->UnitCell->Atoms})
	{
		if ($atom->Name =~ /^$xlinkerReactiveAtom/)
		{
			$xlinkPotential += HCount($atom);
		}
	}
}

# Count xlinks formed during previous runs
my $xlinkCounter = 0;
foreach my $bond (@{$doc->UnitCell->Bonds})
{
	$xlinkCounter++ if ($bond->Name =~ /^xlink/);
}

my $conversion		= 100.0 * $reactedOligomerAtoms / $totalOligomerAtoms;
my $rowCounter		= 0;	# Current row in the study tables

# Check required number of oligomer and xlinker atoms are consistent with conversion
my $targetOligomerAtoms = $totalOligomerAtoms * ($conversionTarget / 100) - $reactedOligomerAtoms;
$textDoc->Append( "Conversion = percent of reactive oligomer atoms that have reacted\n");
$textDoc->Append( "Conversion target = $conversionTarget, Current conversion = $conversion\n");
$textDoc->Append( "Total number of oligomer atoms to react: $targetOligomerAtoms \n");
$textDoc->Append( "Reactant atoms: oligomer $reactiveOligomerAtoms, xlinker $reactiveXLinkerAtoms\n");
$textDoc->Save;
die "Need more xlinkers to achieve specified conversion\n" 
	if ($xlinkPotential < $targetOligomerAtoms);

###########################################################################################
# One time equilibration

if ($one_time_equilibration > 0)
{
	my $steps = ($one_time_equilibration * PICO_TO_FEMTO / $timeStep);
	$textDoc->Append("\nOne-time equilibration\n");
	my $results = ForciteDynamics($doc, $steps, "NVT");
	$results->Trajectory->Delete;
	my $results = ForciteDynamics($doc, $steps, "NPT");
	$results->Trajectory->Delete;
}

###########################################################################################
# Main crosslinking loop
# Increment reaction radius
$textDoc->Append("Entering main crosslinking loop\n");
$textDoc->Save;

for (my $RxnRadius = $MinRxnRadius; $RxnRadius <= $MaxRxnRadius; $RxnRadius += $StepRxnRadius) 
{
	# Base name for the structure	
	my $xsdNameDist = sprintf("%s_R%.2f", $rootName, $RxnRadius);

  	# Equilibrate for each new radius (except first)
  	if ($RxnRadius > $MinRxnRadius)  
  	{
		$textDoc->Append( "Equilibrating at new radius\n");
		$doc->Name = $xsdNameDist . "_init";
		ForciteGeomOpt($doc, 20000);
		my $steps = ($straightDynamicsTime * PICO_TO_FEMTO / $timeStep);
		my $results = ForciteDynamics($doc, $steps, "NPT");
		$results->Trajectory->Delete;
  	}

	# Iterate crosslinking at each radius until one of:
	# A) Maximum number of iterations is reached
	# B) No new xlinks formed
	# C) Conversion target is reached
	for (my $iteration = 1; $iteration <= $IterationsPerRadius; $iteration++)
	{
	
		$textDoc->Append( "\n\n##########################################################\n");
		$textDoc->Append( "###### Radius $RxnRadius, iteration $iteration\n");
		$textDoc->Append( "##########################################################\n\n");
		$textDoc->Save;
			
  		$doc->Name = $xsdNameDist."_".$iteration;

		# Create the new bonds in the structure				
		my $numBonds = createNewXlinks($doc, $RxnRadius);

		# Update conversion
		my $reactedOligomerAtoms  = 0;
		foreach my $atom (@{$doc->UnitCell->Atoms})
		{
			$reactedOligomerAtoms++ if ($atom->Name =~ /^$oligomerReactiveAtom-\d/);
		}
		$conversion = 100 * ($reactedOligomerAtoms/$totalOligomerAtoms);
		$textDoc->Append(sprintf "\nConversion= %.01F %%\n", $conversion);				
		$textDoc->Save;
			
		# If there are no new bonds, exit loop and go to next radius
		if ($numBonds == 0)
		{
			$textDoc->Append("No new bonds created, increasing reaction distance\n");
			last;
		}
		
		# Perturbation to remove long bonds that may have been generated
		optimizeAndPerturb($doc);

		# Generate some cross link statistics
		xlinkStatistics($doc, $RxnRadius, $rowCounter);	
		maxBondEnergy($doc, $RxnRadius, $rowCounter) if ($UseMaxBondEnergy);

		# Save structure to study table
		$textDoc->Append("Saving intermediate structure to study table\n");				
		$doc->InsertInto($structureTable);
		$structureTable->Cell($rowCounter,1) = $RxnRadius;
		$structureTable->Cell($rowCounter,2) = $iteration;
		$structureTable->Cell($rowCounter,3) = $conversion;

		# short dynamics run to record some thermodynamic properties
		my $analysis_doc = Documents->New("analyze.xsd"); 
		$analysis_doc->CopyFrom($doc);
		$textDoc->Append( "\n\nRunning additional dynamics for analysis\n");
		my $steps = ($analyzeDuration * PICO_TO_FEMTO / $timeStep);
		my $freq = int($steps/20);
		my $results = ForciteDynamics($analysis_doc, $steps, "NPT", (TrajectoryFrequency => $freq) );								
		getTrajTempAndPressure($results, $rowCounter, $RxnRadius);
		getEnergies($results,$rowCounter);
		$analysis_doc->Delete;
		$results->Trajectory->Delete;
		$rowCounter++;
				
		# Report the time taken by this iteration
		$timeDoc->Append(sprintf "%8.2f %2d %8.1f %8.2f %8.1f\n", 
			$RxnRadius, $iteration, (time-$^T)/3600, 
			(time-$segtime)/3600, $conversion);
		$segtime = time;
		
		# If conversion target is reached, delete excess and quit loop			
		if ($conversion >= $conversionTarget) 
		{
			# Calculate the number of bonds to delete				
			my $numbondsDelete = $xlinkCounter - $reactedOligomerAtoms - $targetOligomerAtoms;			
			$textDoc->Append(sprintf "\nCrosslinking complete. Actual conversion = %0.1F ".
				"Target conversion = %0.1F\n\n", $conversion, $conversionTarget);
			
			if ($deleteExcessXlinks and $numbondsDelete > 0) 
			{				
				$textDoc->Append("Randomly removing $numbondsDelete xlinks to meet ".
					"conversion target\n");	
				# Delete the excess bonds and calculate the final statistics
				deleteExcessBonds($doc, $numbondsDelete);
				xlinkStatistics($doc, "Final", $rowCounter);
			} 
			else 
			{ 				
				$textDoc->Append(sprintf "There are no excess bonds to delete\n");
			}
			$textDoc->Save;
			last;
		}

		# Save all docs case you want to terminate the script and not lose data		
		Documents->SaveAll;
	
	} # next iteration
	
	last if ($conversion >= $conversionTarget);

} # next radius
 	
# Rename the final xsd with a unique name
$doc->Name = $rootName."_final";

# Calculate the bond distribution
analyzeBonds($doc);

# Create set of xlinked atoms.
XlinkSet($doc);

$textDoc->Append( "\n##############################################################\n");
$textDoc->Append( "There are $xlinkCounter crosslinks in the system\n");
$textDoc->Append( "Final conversion $conversion %\n");
$textDoc->Append( "##############################################################\n");
$textDoc->Save;

# Report total time
my $time_hr = (time-$^T)/3600;
$textDoc->Append(sprintf ("\nTotal time %.2f hr\n", $time_hr));
$textDoc->Append( "Calculation is complete\n");
Documents->SaveAll;



##########################################################################################################
#
#		END OF MAIN
#
##########################################################################################################


#########################################################################################################

# Creates 'not-R1' and 'not-R2' sets 
# These are used in the close-contacts calculation, done in set-exclusion mode. 
# Finds contacts between:
# (A) R1 and R2 atoms in the unit cell
# (B) (unfortunately) R1 or R2 atoms in the unit cell and image atoms in adjacent cells.

sub createReactiveAtomSets 
{
	my $doc = shift;

	$textDoc->Append("  createReactiveAtomSets\n");

	# Initialise reactive atom counters	
	my $R1Counter = 0;
	my $R2Counter = 0;
	
	# Create two perl arrays for atoms	
	my @notR1;
	my @notR2;

	# Create two sets based on atom names
	# One contains all atoms except R1 and the other all except R2
	my $atoms = $doc->UnitCell->Atoms;
	foreach my $atom (@$atoms) 
	{
		# Check to see if the atom is a reactive atom	
		if (isReactiveR1($atom)) 
		{					
			push (@notR2, $atom);
			$R1Counter++;		
		} 
		elsif (isReactiveR2($atom)) 
		{					
			push (@notR1, $atom);
			$R2Counter++;		
		} 
		else 
		{		
			push (@notR1, $atom);
			push (@notR2, $atom);
		}	
	}

	# Create the sets based on the atom arrays and hide them
	my $notR1Set = $doc->CreateSet("notR1", \@notR1);
	my $notR2Set = $doc->CreateSet("notR2", \@notR2);
	$notR1Set->IsVisible = 0;
	$notR2Set->IsVisible = 0;

	$textDoc->Append("    $R1Counter oligomer atoms unreacted\n");
	$textDoc->Append("    $R2Counter xlink atoms unreacted\n\n");
	$textDoc->Save;
		
	return ($doc, $R1Counter, $R2Counter);
}

#########################################################################################################

# Determine whether this is an oligomer reactive atom
# It depends if react_multi is being used. If so, we check attached hydrogens.

sub isReactiveR1
{
	my $atom = shift;
	my $name = $atom->Name;
	if ($name =~ /^$oligomerReactiveAtom/)
	{
		return TRUE if ($name eq "$oligomerReactiveAtom");
		return TRUE if ($react_multi_oligomer and HCount($atom) > 0);
	}
	return FALSE;
}

#########################################################################################################

# Determine whether this is an xlinker reactive atom
# It depends if react_multi is being used. If so, we check attached hydrogens.

sub isReactiveR2
{
	my $atom = shift;
	my $name = $atom->Name;
	if ($name =~ /^$xlinkerReactiveAtom/)
	{
		return TRUE if ($name eq "$xlinkerReactiveAtom");
		return TRUE if ($react_multi_xlinker and HCount($atom) > 0);
	}
	return FALSE;
}

#########################################################################################################

# This was added to handle restarts more gracefully
# Returns the number of atoms with names like R1-38 and R2-7

sub countReactedAtoms
{
	my ($doc1) = @_;
	my $nO = 0; my $nXL = 0;
	my $atoms = $doc1->UnitCell->Atoms;
	foreach my $atom (@$atoms) 
	{
		$nO++ if ($atom->Name =~ /^$oligomerReactiveAtom-\d+$/);
		$nXL++ if ($atom->Name =~ /^$xlinkerReactiveAtom-\d+$/);
	}
	return ($nO, $nXL);
}

#########################################################################################################

# Crosslink R1-R2 close-contact atoms either with restraints or with real bonds
# Atoms are renamed to prevent further crosslinking (unless multi option is on)

sub createNewXlinks 
{
	my $doc1 = shift;
	my $distance = shift;
	
	my $t0 = time;
	$textDoc->Append("createNewXlinks\n");	

	# Update the reactive sets
	($doc1, my $R1Count, my $R2Count) = createReactiveAtomSets($doc1);
			
	# Recalculate close contacts using set-exclusion, based on current reaction 
	# distance cutoff and updated sets
	Tools->BondCalculation->ChangeSettings([
		DistanceCriterionMode	=> "Absolute",
		ExclusionMode		=> "Set", 
		MaxAbsoluteDistance	=> $distance
	]);
	my $closeContacts = $doc1->CalculateCloseContacts;		
		
	# Delete contacts with non-R atoms in adjacent cells
	foreach my $closeContact (@$closeContacts) 
	{
		my $atom1 = $closeContact->Atom1;
		my $atom2 = $closeContact->Atom2;	
		if ($atom1->Name =~ m/^$xlinkerReactiveAtom/)
		{
			$atom1 = $closeContact->Atom2;
			$atom2 = $closeContact->Atom1;
		}
		# Delete unless both atoms are reactive and of opposite types
		$closeContact->Delete unless ( isReactiveR1($atom1) and isReactiveR2($atom2) );
	}

	# Randomize the close contacts	
	my @ReactiveContacts = shuffle(@$closeContacts);
		
	$textDoc->Append("  ".scalar(@ReactiveContacts)." reactive close-contacts\n");	


	# Go through each close contact and create the bonds
	my $newBondCounter = 0;
	my $lockedAtoms = $doc1->UnitCell->BestFitLines->Molecules;
	
	foreach my $closeContact (@ReactiveContacts) 
	{
		my $atom1 = $closeContact->Atom1;
		my $atom2 = $closeContact->Atom2;
		if ($atom1->Name =~ m/^$xlinkerReactiveAtom/)
		{
			$atom1 = $closeContact->Atom2;
			$atom2 = $closeContact->Atom1;
		}

		# Exclude multiple reactions on the same atom in the same round
		next if ($atom1->Name =~ /_LOCKED$/ or $atom2->Name =~ /_LOCKED$/);

		# Create the xlink (real or virtual)				
		if ($UseRestraintBonds)
		{
			createNewBondRestraint($doc1, $atom1, $atom2);
		} 
		else 
		{
			createNewBond($doc1, $atom1, $atom2);
		}
		$newBondCounter++;
		
		# Lock these atoms so they don't react again
		$atom1->Name .= "_LOCKED";
		$atom2->Name .= "_LOCKED";
		$lockedAtoms->Add($atom1);
		$lockedAtoms->Add($atom2);
	}
	
	# Unlock the xlink atoms
	foreach my $atom (@$lockedAtoms)
	{
		$atom->Name =~ s/_LOCKED//;
	}
	$textDoc->Append("  $newBondCounter links formed (excluding multiple to same atom)\n");	
	
	EquilibrateRestraintXlinks($doc1) if ($UseRestraintBonds and $newBondCounter > 0);

	$textDoc->Append( "  $newBondCounter new xlink bonds\n\n");
	$textDoc->Save;
	
	# Adjust hydrogens
	$doc1->AdjustHydrogen;
	
	# Regenerate charge groups
	if ($chargeMethod eq "Group based")
	{
		$doc1 = DivideAndConquer($doc1, $Forcite);
	}
	
	# Remove the close contacts and sets for the next cycle	
	$doc1->UnitCell->CloseContacts->Delete;
	$doc1->UnitCell->Sets->Delete;
	
	# Geometry optimize
	$textDoc->Append("  ");
	ForciteGeomOpt($doc1, 2000);
	
	# Report time
	$textDoc->Append(sprintf "\ncreateNewXlinks took %d seconds\n\n", time-$t0); 
	$textDoc->Save;

	return ($newBondCounter);
}

#########################################################################################################

# Impose harmonic distance restraint between two atoms

sub createNewBondRestraint
{	
	my ($doc1, $atom1, $atom2) = @_;	
	
	# measure the distance between reacting atoms			
	my $distance = $doc1->CreateDistance([$atom1, $atom2]);
	
	# create restraint and set initial equilibrium bond length and force constants
	# (these are updated appropriately in the equilibration routine)					
			
	my $restraint = $distance->CreateRestraint("Harmonic");
	$restraint->HarmonicForceConstant = 0;
	$restraint->HarmonicMinimum = $distance->Distance;
	
	$textDoc->Append( sprintf "  createNewBondRestraint between %s and %s\n", 
		$atom1->Name, $atom2->Name);
}

#########################################################################################################

# Create the new xlink bond and change the display style and name of the link
# Also adjust chemistry: epoxy rings and condensates
# Expects $atom1 to be from oligomer and $atom2 from xlinker

sub createNewBond
{	
	my ($doc1, $atom1, $atom2)= @_;	

	# Open the epoxy ring	
	deleteEpoxyBond($atom1) if ($openRing);

	# Remove condensation OH group	
	if ($remove_condensation) 
	{
		CondenseLink($atom1);
		CondenseLink($atom2);
	}

	# Create the new bond
        $xlinkCounter++;
	my $newBond = $doc1->CreateBond($atom1, $atom2, "Single", ([Name => "xlink-".$xlinkCounter]));        
        
        # Set the display style of the created bond to ball and stick       
        $atom1->Style = "Ball and stick";
        $atom2->Style = "Ball and stick";
        
        # Append xlink index to each atom name (will not affect future xlinking)
        $atom1->Name .= "-".$xlinkCounter;
        $atom2->Name .= "-".$xlinkCounter;
        
        $textDoc->Append( sprintf "    Created bond between %s and %s \n\n", $atom1->Name, $atom2->Name);
}

#########################################################################

# Count attached hydrogens

sub HCount
{
	my $atom = shift;
	my $n = 0;
	foreach (@{$atom->AttachedAtoms})
	{
		$n++ if ($_->ElementSymbol eq "H");
	}
	return $n;
}

#########################################################################
# Identify and remove OH group attached to given atom
# Rules:
# (A) First attached atom must by oxygen and have two bonds
# (B) Second attached atom must be hydrogen
# (C) Only one such match for rules A and B is allowed

sub CondenseLink
{
	my $xlinkAtom = shift;
	
	my $Oatom; 
	my $Hatom;
	my $nO = 0;
	my $nH = 0;
	my $status = 0;
	
	foreach my $atom1 (@{$xlinkAtom->AttachedAtoms})
	{
		if ($atom1->ElementSymbol eq "O" and $atom1->Bonds->Count == 2)
		{
			$Oatom = $atom1;
			$nO++;
			foreach my $atom2 (@{$atom1->AttachedAtoms})
			{
				if ($atom2->ElementSymbol eq "H")
				{
					$Hatom = $atom2;
					$nH++;
				}
			}
		}
	}

	if ($nH == 1 and $nO == 1)
	{
		$Oatom->Delete;
		$Hatom->Delete;
		$status = 1;
		if (DEBUG) { $textDoc->Append( sprintf "  CondenseLink: deleted OH group from %s\n", $xlinkAtom->Name) };
	}
	
	return $status;
}

#######################################################################################################################

# Delete bond between specified atom and the $deleteAtom

sub deleteEpoxyBond 
{
	my $epoxyatom = shift;
	
	my $n = 0;
	foreach my $atom (@{$epoxyatom->AttachedAtoms}) 
	{
		if ($atom->ElementSymbol eq "$deleteAtom")
		{
			foreach my $bond (@{$atom->Bonds}) 
			{
				if ($bond->Atom1->Name eq $epoxyatom->Name or $bond->Atom2->Name eq $epoxyatom->Name)
				{
					$textDoc->Append(
						sprintf "    Deleting epoxide bond between %s and %s\n",
						$bond->Atom1->Name, $bond->Atom2->Name ) 
					if (DEBUG);
					$bond->Delete;
					$n++;
				} 
			}
		}
	}
	warn "deleteEpoxyBond: deleted $n bonds" unless ($n == 1);
}


#######################################################################################################

# Return maximum bond energy
# Efficient algorithm that calculates the energy only for the shortest bond of each type
# Requires: $textDoc, $statTable, $nstatsheets

sub maxBondEnergy
{
	my ($doc1, $distance, $row) = @_;
	my $t0 = time;
	my $bonds = $doc1->UnitCell->Bonds;
	$textDoc->Append(sprintf "Analyzing %d bonds in the unit cell\n", $bonds->Count)
		if (DEBUG > 1);
	
	# First make a hash of bond lengths by type
	my %length;
	foreach my $bond (@$bonds)
	{
		my $sequence = bondsequence($bond);
		#printf "%d %s %s\n", $i, $bond->Name, $sequence if ($i%50 == 0);
		push @{ $length{$sequence} }, $bond->Length;
	}
	my @bondTypes = keys %length;
	#print "@bondTypes\n";
	$textDoc->Append(sprintf "Found %d distinct bond types\n", scalar @bondTypes)
		if (DEBUG > 1);

	# Create a temporary document for energy calcs
	my $tmpDoc = Documents->New("bondEnergy.xsd");
	my $a1 = $tmpDoc->CreateAtom("C", Point());
	my $a2 = $tmpDoc->CreateAtom("C", Point(X => 1.5));
	my $bond = $tmpDoc->CreateBond($a1, $a2, "Single");
	my $Forcite1 = Modules->Forcite;
	$Forcite1->ChangeSettings([ 
		CurrentForcefield	=> $forcefield, 
		WriteLevel		=> "Silent", 
		AssignForcefieldTypes	=> "Yes"]);

	# One energy calculation per bond type
	my $maxBondEnergy = 0;
	my $bondLength; 
	my $bondType;
	foreach my $type (keys %length)
	{
		# Sort each list of lengths in reverse order
		my @lengths = reverse sort @{ $length{$type} };
		
		# Set atom types and bond length in energy doc
		my @fftype = split /,/, $type;
		$a1->ForcefieldType = $fftype[0];
		$a2->ForcefieldType = $fftype[1];
		$a2->X = $lengths[0];
		
		# Calculate energy
		my $results = $Forcite1->Energy->Run($tmpDoc);
		my $bondEnergy = $tmpDoc->BondEnergy;
		#printf "%s %f %f\n", $type, $bond->Length, $bondEnergy;
		
		# Update max value and associated properties of interest
		if ($maxBondEnergy < $bondEnergy)
		{
			$maxBondEnergy = $bondEnergy;
			$bondLength = $lengths[0];
			$bondType = $type;
		}
	}
	
	# Delete the energy document
	$tmpDoc->Discard;
	
	# Output to study table
	if ($row == 0)
	{
		my $sheet = $statTable->InsertSheet($nstatsheets,"Max Bond Energy");
		$nstatsheets++;
		$sheet->ColumnHeading(0) = "Reaction Radius (A)";
		$sheet->ColumnHeading(1) = "Percent Conversion";
		$sheet->ColumnHeading(2) = "Max Bond Energy (kcal/mol)";
	}
	my $sheet = $statTable->Sheets("Max Bond Energy");
	$sheet->InsertRow;
	$sheet->Cell($row,0) = $distance;
	$sheet->Cell($row,1) = $conversion;
	$sheet->Cell($row,2) = $maxBondEnergy;

	# Report on progress
	if (DEBUG > 0)
	{
		$textDoc->Append(sprintf "\nmaxBondEnergy, %d seconds, %s: %f kcal/mol\n", 
			time-$t0, $bondType, $maxBondEnergy); 
		$textDoc->Save;
	}

	return ($maxBondEnergy, $bondType, $bondLength);
}

#######################################################################################################
# Return canonical bond sequence - i.e. comma separated, alphabetized, fftype list

sub bondsequence
{
	my $bond = shift;
	return join ",", sort ($bond->Atom1->ForcefieldType, $bond->Atom2->ForcefieldType);
}
	
#######################################################################################################

# Compute stats on reactive atoms from the xlinker and oligomer molecules
# Requires globals: $statTable, $textDoc, $nstatsheets,
# $xlinkerName, $oligomerName, $xlinkerReactiveAtom, $oligomerReactiveAtom

sub xlinkStatistics 
{
	my ($doc1, $distance, $row) = @_;

	my $t0 = time;
	
	# Rename the xlinker and oligomer molecules at the beginning
	if ($row == 0)
	{
		foreach my $atom (@{$doc1->UnitCell->Atoms})
		{
			if ($atom->Name eq "$xlinkerReactiveAtom")
			{
				$atom->Ancestors->Molecule->Name = $xlinkerName;
			}
			elsif ($atom->Name eq "$oligomerReactiveAtom")
			{
				$atom->Ancestors->Molecule->Name = $oligomerName;
			}
		}
		
		# Append an index to each oligomer molecule name
		my $oligCounter = 0;
		foreach my $mol (@{$doc1->UnitCell->Molecules}) 
		{	
			if ($mol->Name eq "$oligomerName") 
			{
				++$oligCounter;
				$mol->Name .= "_$oligCounter";
			}
		}
	}
	
	# Initialize some counters
	my $intraXLinks	= 0;
	my $nXlinker = 0;
	my $nReactedAtoms = 0;
	
	# Distribution of number of reacted R2 atoms in each xlinker
	my $max = 10; # hard coded (assumes there can never be more than this many bonds per xlinker)
	my @reactedXlinkers;
	for (my $i=0; $i<=$max; $i++) { $reactedXlinkers[$i]=0; }
	
	# For each xlink molecule, grab the names of the molecules attached to the reactive
	# atoms. Store these in an array, @xlOligomer
	
	foreach my $mol (@{$doc1->UnitCell->Molecules}) 
	{
		my @xlOligomer = ();	
		next unless ($mol->Name eq "$xlinkerName");

		# Search reactive atoms in the xlinker molecule
		foreach my $atom (@{$mol->Descendants->Atoms}) 
		{
			next unless ($atom->Name =~ /^$xlinkerReactiveAtom/);
			# Array of oligomer names attached to this xlinker
			foreach my $attachedAtom (@{$atom->AttachedAtoms}) 
			{
				next unless ($attachedAtom->Name =~ /^$oligomerReactiveAtom/);
				push @xlOligomer, $attachedAtom->Ancestors->Molecule->Name;
			} 
		}
			
		# update xlinker distbn
		my $numReactedAtoms = scalar(@xlOligomer);
		$reactedXlinkers[$numReactedAtoms]++;

		# count number of 'intra' xlinks - when same xlinker and oligomer 
		# are linked multiple times
		for (my $i=0; $i<$numReactedAtoms-1; $i++)
		{
			for (my $j=$i+1; $j<$numReactedAtoms; $j++)
			{
				++$intraXLinks if ($xlOligomer[$i] eq  $xlOligomer[$j]); 
			}
		}
			
		$nReactedAtoms += $numReactedAtoms;
		$nXlinker++;
	} #next mol
	
	# Calculate number of reacted xlinker molecules from non-zero elements of distbn
	my $nReactedMols = 0;
	for (my $i=1; $i<=$max; $i++)
	{
		$nReactedMols += $reactedXlinkers[$i];
	}
	my $xlRatio = $nReactedAtoms / $nXlinker;

	# Initialize xlinker sheet on first time
	$statTable->ActiveSheetIndex = 0;
	if ($row == 0)
	{
		$statTable->Title = "Xlinkers";
		$statTable->ColumnHeading(0) = "Reaction Radius (A)";
		$statTable->ColumnHeading(1) = "xlinkers reacted (n=$nXlinker)";
		$statTable->ColumnHeading(2) = "Percent xlinkers reacted (n=$nXlinker)";
		$statTable->ColumnHeading(3) = "Intramolecular xlinks";
		$statTable->ColumnHeading(4) = "Reacted xlinker atoms per xlinker";
	}

	# Add xlinker stats to study table
	$statTable->Cell($row,0) = $distance;
	$statTable->Cell($row,1) = $nReactedMols;
	$statTable->Cell($row,2) = 100 * $nReactedMols / $nXlinker;
	$statTable->Cell($row,3) = $intraXLinks;
	$statTable->Cell($row,4) = $xlRatio;
	for (my $i=0; $i<=$max; $i++)
	{
		$statTable->ColumnHeading(5+$i) = "Percent xlinkers with $i reactions" if ($row == 0);
		$statTable->Cell($row,5+$i) = 100*$reactedXlinkers[$i]/$nXlinker;
	}

	$textDoc->Append( "\n##########################################################\n");
	$textDoc->Append( "################## S T A T I S T I C S ###################\n");
	$textDoc->Append( "##########################################################\n\n");
		
	$textDoc->Append( "\n#######   Statistics for the xlinker   ########\n\n");

	$textDoc->Append("$nReactedMols of $nXlinker crosslinker molecules have reacted\n");
	$textDoc->Append("     $intraXLinks formed intramolecular cross links\n");
	$textDoc->Append(sprintf "     %.2f reacted xlinker atoms per xlinker\n\n", $xlRatio);


	############################################################################
	# Now do nearly the same thing for the oligomers
	
	my $nOligomer = 0;
	my $nReactedAtoms = 0;
	my $max = 10; 
	my @reactedOligomers;
	for (my $i=0; $i<=$max; $i++) { $reactedOligomers[$i]=0; }
	
	# For each oligomer molecule, grab the names of the molecules attached to the reactive
	# atoms. Store these in an array, @xlXlinker
	
	foreach my $mol (@{$doc1->UnitCell->Molecules}) 
	{
		my @xlXlinker = ();	
		next unless ($mol->Name =~ /^$oligomerName/);

		# Grab the reactive atoms in the oligomer molecule
		foreach my $atom (@{$mol->Descendants->Atoms}) 
		{
			next unless ($atom->Name =~ /^$oligomerReactiveAtom/);
			# Array of xlinker names attached to this oligomer
			foreach my $attachedAtom (@{$atom->AttachedAtoms}) 
			{
				next unless ($attachedAtom->Name =~ /^$xlinkerReactiveAtom/);
				push @xlXlinker, $attachedAtom->Ancestors->Molecule->Name;
			} 
		}
			
		# update distbn
		my $numReactedAtoms = scalar(@xlXlinker);
		$reactedOligomers[$numReactedAtoms]++;
		$nReactedAtoms += $numReactedAtoms;
		$nOligomer++;
	} #next mol


	# Calculate number of reacted oligomer molecules from non-zero elements of distbn
	my $nReactedMols = 0;
	for (my $i=1; $i<=$max; $i++)
	{
		$nReactedMols += $reactedOligomers[$i];
	}
	my $xlRatio = $nReactedAtoms / $nOligomer;

	# Add new sheet for oligomer data on first time through
	if ($row == 0)
	{
		my $sheet = $statTable->InsertSheet($nstatsheets,"Oligomers");
		$nstatsheets++;
		$sheet->ColumnHeading(0) = "Reaction Radius (A)";
		$sheet->ColumnHeading(1) = "Oligomers reacted (n=$nOligomer)";
		$sheet->ColumnHeading(2) = "Percent reacted (n=$nOligomer)";
		$sheet->ColumnHeading(3) = "Reacted atoms per oligomer";
	}
	
	# Update study table with oligomer data
	my $sheet = $statTable->Sheets("Oligomers");
	$sheet->InsertRow;
	$sheet->Cell($row,0) = $distance;
	$sheet->Cell($row,1) = $nReactedMols;
	$sheet->Cell($row,2) = 100 * $nReactedMols / $nOligomer;
	$sheet->Cell($row,3) = $xlRatio;
	for (my $i=0; $i<=$max; $i++)
	{
		$sheet->ColumnHeading(4+$i) = "Percent oligomers with $i reactions" if ($row == 0);
		$sheet->Cell($row,4+$i) = 100 * $reactedOligomers[$i] / $nOligomer;
	}

	$textDoc->Append( "\n#######   Statistics for the oligomer   ########\n\n");
	$textDoc->Append("$nReactedMols of $nOligomer oligomer molecules have reacted\n");
	$textDoc->Append(sprintf "     %.2f reacted oligomer atoms per oligomer\n\n", $xlRatio);

	$textDoc->Append(sprintf "\nxlinkStatistics %d seconds\n", time-$t0); 
	$textDoc->Save;
}

#########################################################################################################

# Optimization, short NVT dynamics and temperature cycle

sub optimizeAndPerturb 
{
	$textDoc->Append("\noptimizeAndPerturb\n");
	$textDoc->Save; 
	my $t0 = time; 
	my $mdStepCounter = 0; 
	my ($doc1) = @_;
	
	my $cycles 			= 1;
	
	# use the *Results variables to store the results of the eval statements	 
	my $short_dynamics_results 	= undef;
	my $heatCycleResults 		= undef;
	my $coolCycleResults 		= undef;

	my $while_control 		= 0;
	my $short_dynamics_passed 	= undef;

	$textDoc->Append("  ");
	ForciteGeomOpt($doc1, 200);
	
	$textDoc->Append("  ");
	my $results = ForciteDynamics($doc1, 1000, "NVT");
	$mdStepCounter+=1000;
	$results->Trajectory->Delete;

	return $doc1 if ($UseTempCycle == FALSE);


	# Optional annealing run	

	my $steps = ($tempDuration * PICO_TO_FEMTO / $timeStep);
	
	for (my $cycleCounter = 0; $cycleCounter < $cycles; ++$cycleCounter) 
	{
		# take the temperature up		
		for (my $temperature = $startTemp; $temperature <= $highTemp; $temperature += $tempStep) 
		{
			$textDoc->Append( "  Heating up, running at $temperature K\n  ");
			$textDoc->Save;
			TemperatureCycleStep($doc1, $steps, $temperature);
			$mdStepCounter += 2*$steps;
		}
		
		# take the temperature down
		for (my $temperature = $highTemp; $temperature >= $lowTemp; $temperature -= $tempStep) 
		{			
			$textDoc->Append( "  Cooling down, running at $temperature K\n  ");	
			$textDoc->Save;
			TemperatureCycleStep($doc1, $steps, $temperature);
			$mdStepCounter += 2*$steps;
		}
	}
	
	ForciteGeomOpt($doc1, 500);
	if (DEBUG) {
		$textDoc->Append( sprintf "optimizeAndPerturb %d total steps, %d seconds\n", 
			$mdStepCounter, time-$t0 ); 
	}
	$textDoc->Save; 
}


#######################################################################################################

# Single step in a temperature cycle: NVT and then NPT dynamics at specified temperature
# Requires globals: $tempDuration, $timeStep, $Forcite, $cycleSteps, $textDoc, $Quality

sub TemperatureCycleStep 
{
	my $doc1 = shift;
	my $steps = shift;
	my $temperature = shift;
	
	my $results = ForciteDynamics($doc1, $steps, "NVT", ( Temperature => $temperature ) );
	$results->Trajectory->Delete;
	
	my $results = ForciteDynamics($doc1, $steps, "NPT", ( 
		Temperature		=> $temperature,
		InitialVelocities  	=> "Current"
	) );
	$results->Trajectory->Delete;
}

#########################################################################################################

# Deletes the excess bonds to get the appropriate conversion rate	

sub deleteExcessBonds 
{
	my $doc1		= shift;	
	my $bondsToDelete 	= shift;
	
	$textDoc->Append( "Deleting $bondsToDelete bonds\n");
	
	# Get all the bonds in an array	
	my @xlinkBonds = ();
	
	foreach my $bond (@{$doc1->UnitCell->Bonds}) {
	
		if ($bond->Name =~ /^xlink/) { push (@xlinkBonds, $bond); }
		
	}	
	my @shuffledXLinkBonds =();
	
	# Randomize the bond array	
	@shuffledXLinkBonds = shuffle(@xlinkBonds);
		
	# Delete the last X bonds	
	for (my $counter = 0; $counter < $bondsToDelete; ++$counter) {
		
		$textDoc->Append(sprintf ("Deleting bond length %0.2F\n",@shuffledXLinkBonds[-1]->Length));
		
		# Change the display stlye back to line
		@shuffledXLinkBonds[-1]->Atom1->Style = "Line";
		@shuffledXLinkBonds[-1]->Atom2->Style = "Line";
		my $atom1_old_xlink_atom = @shuffledXLinkBonds[-1]->Atom1;
		my $atom2_old_xlink_atom = @shuffledXLinkBonds[-1]->Atom2;
		@shuffledXLinkBonds[-1]->Delete;
		
		pop (@shuffledXLinkBonds);		
	}	
	$textDoc->Append( "\n\n");	
}

#########################################################################################################

# Analyze bond length distributions

sub analyzeBonds
{
	my $doc1 = shift;
	
	# Calculate the distribution of all the bonds	
	my $bondAnalysis = $Forcite->Analysis->LengthDistribution($doc1, [
		LengthDistributionUseBonds	=> "Yes"
	]);	
	$bondAnalysis->LengthDistributionChartAsStudyTable->Delete;	
	$bondAnalysis->LengthDistributionChart->Name = "AllBonds";
	
	# Create a set of distances for all the x-link bonds
	my @distances;
	foreach my $bond (@{$doc1->UnitCell->Bonds}) 
	{	
		if ($bond->Name =~ /^xlink/) 
		{
			my $distance = $doc1->CreateDistance([$bond->Atom1, $bond->Atom2]);		
			push @distances, $distance;			
		}	
	}
	return unless ( scalar(@distances) > 0 );
	$doc1->CreateSet("xlink distances", \@distances);
	
	# Now analyze the xlink distances only	
	my $bondAnalysis = $Forcite->Analysis->LengthDistribution($doc1, [
		LengthDistributionSetA	=> "xlink distances"
	]);
	$bondAnalysis->LengthDistributionChartAsStudyTable->Delete;
	$bondAnalysis->LengthDistributionChart->Name = "XlinkBonds";
	$doc1->UnitCell->Distances->Delete;
}

#########################################################################################################

# Gradually increase the restraint force and reduce the restraint distance
# Each iteration includes geometry optimization and NPT dynamics to relax the system
# Finish by replacing the restraints with bonds

sub EquilibrateRestraintXlinks 
{
	my $t0 = time;
	if (DEBUG) { $textDoc->Append("\n  EquilibrateRestraintXlinks\n") };
	my ($doc) = @_;

	my $ForceConstantInc = $RestraintForceConstant/$nRestraintBondingStages;

	# loop over changes in restraint paramters	
	for (my $i = 1; $i <= $nRestraintBondingStages; $i++) 
	{
		$textDoc->Append("\n    Stage $i\n");
		# Tighten restraints (increase force constant & decrease equilibrium distance)
		my $restraints = $doc->UnitCell->Restraints;
		foreach my $restraint (@$restraints) 
		{
			my $k = $restraint->HarmonicForceConstant  + $ForceConstantInc;
			my $b0inc = ($restraint->HarmonicMinimum - $RestraintBondingTargetLength)
					/ ($nRestraintBondingStages+1-$i);
			my $b0 = $restraint->HarmonicMinimum - $b0inc;
					
			$restraint->HarmonicForceConstant 	= $k;
			$restraint->HarmonicMinimum 		= $b0;
			
			if (DEBUG) { $textDoc->Append(sprintf ("    Setting restraint to K=%f and B=%f\n",
					$k,$b0)) };
			 
		}
		
		$textDoc->Append("    ");
		ForciteGeomOpt($doc, 20000);
		$textDoc->Append("    ");
		#$doc = relaxNPT($doc);
		my $steps = ($relax_length * PICO_TO_FEMTO / $timeStep);
		my $results = ForciteDynamics($doc, $steps, "NPT",(TimeStep=> 0.5));
		$results->Trajectory->Delete;
	}	
	$textDoc->Append("\n");

	# Now do the full bonding using the restraint objects to identify the atoms involved
	my $restraints = $doc->UnitCell->Restraints;
	foreach my $restraint (@$restraints) 
	{
		if (RestraintType($restraint) eq "distance") 
		{
			my $dist = $restraint->Ancestors->Distance;
			my $atom1 = $dist->DistanceNodeI;
			my $atom2 = $dist->DistanceNodeJ;		 			
			my $atom1_name = $atom1->Name;
			my $atom2_name = $atom2->Name;
			
        		$textDoc->Append(
        			sprintf "    Creating xlink %d between %s and %s and deleting restraint\n",
        				$xlinkCounter+1, $atom1_name, $atom2_name)
        		if (DEBUG);
        		
        		createNewBond($doc, $atom1, $atom2);
						
			$restraint->Delete;
			$dist->Delete;
		}
	}
		
	if (DEBUG) 
	{ 
		$textDoc->Append(sprintf "\n  EquilibrateRestraintXlinks took %d seconds\n\n", time-$t0); 
		$textDoc->Save; 
	}
}

#########################################################################################################

sub RestraintType
{
    my ($restraint) = @_;
    my $type = "unknown";
    eval {
        my $ancestors = $restraint->Ancestors;
        if ( $ancestors->Distance->Count ) {
            $type = "distance";
        }
        elsif ( $ancestors->Angle->Count ) {
            $type = "angle";
        }
        elsif ( $ancestors->Torsion->Count ) {
            $type = "torsion";
        }
    };
    return $type;
}


###################################################################################################################

sub getEnergies 
{

	my $doc = shift;
	my $row_counter = shift;
	my $trj = $doc->Trajectory;
	my @bond_energies = ();
	my @angle_energies = ();
	my @potential_energies =();
	for (my $frame_counter = 1; $frame_counter <= $trj->NumFrames; ++$frame_counter) 
	{
	
		#Sets the current frame and creates a new document
	
		$trj->CurrentFrame = $frame_counter;
		
		# calculate energies for this snapshot
		#my $frame_doc->CopyFrom($trj);
		Modules->Forcite->Energy->Run($trj);
		my $bond_energy = $trj->BondEnergy;
		my $angle_energy = $trj->AngleEnergy;
		my $potential_energy = $trj->PotentialEnergy;
		
		# push values into the appropriate array for subsequent analysis
		
		push (@bond_energies,$bond_energy);
		push (@angle_energies, $angle_energy);
		push (@potential_energies, $potential_energy);
				
	}
	
	# calcaulte average and std dev.
	
	my ($avg_bond, $sd_bond)   = calculateStatistics(@bond_energies);
	my ($avg_angle, $sd_angle) = calculateStatistics(@angle_energies);
	my ($avg_pe, $sd_pe)       = calculateStatistics(@potential_energies);
	
	$textDoc->Append( sprintf "Bond energy  %11.5g %11.5g\n",   $avg_bond,  $sd_bond);  	
	$textDoc->Append( sprintf "Angle energy %11.5g %11.5g\n",   $avg_angle, $sd_angle);  	
	$textDoc->Append( sprintf "Pot. energy  %11.5g %11.5g\n\n", $avg_pe,    $sd_pe);  
	
	# write these to study table
	my $sheet = $statTable->Sheets("Thermo");
	if ($row_counter == 0)
	{
		$sheet->ColumnHeading(5) = "Potential Energy (kcal/mol)";
		$sheet->ColumnHeading(6) = "Std Dev";
		$sheet->ColumnHeading(7) = "Bond Energy (kcal/mol)";
		$sheet->ColumnHeading(8) = "Std Dev";
		$sheet->ColumnHeading(9) = "Angle Energy (kcal/mol)";
		$sheet->ColumnHeading(10) = "Std Dev";
	}

	$sheet->Cell($row_counter,5) = $avg_pe;
	$sheet->Cell($row_counter,6) = $sd_pe;
	$sheet->Cell($row_counter,7) = $avg_bond;
	$sheet->Cell($row_counter,8) = $sd_bond;
	$sheet->Cell($row_counter,9) = $avg_angle;
	$sheet->Cell($row_counter,10) = $sd_angle;
}

#######################################################################################################################

# Compute temperature and pressure statistics from frames in trajectory
# Requires globals: $statTable, $nstatsheets

sub getTrajTempAndPressure
{
	my $dynamicsResults	= shift;
        my $row_counter		= shift;
        my $distance		= shift;
        
        # Forcite analysis
	my $T_analysis = Modules->Forcite->Analysis->Temperature($dynamicsResults->Trajectory, 
			[ComputeProfile => "Yes", ComputeBlockAverages => "No"]);
	my $P_analysis = Modules->Forcite->Analysis->Pressure($dynamicsResults->Trajectory,
			[ComputeProfile => "Yes", ComputeBlockAverages => "No"]);
	my $T_std = $T_analysis->TemperatureChartAsStudyTable;
	my $P_std = $P_analysis->PressureChartAsStudyTable;

	# Push data from study tables into perl arrays
	my @T = ();
	my @P = ();
	for (my $row = 0; $row < $T_std->RowCount; ++$row) 
	{
		push (@T, $T_std->Cell($row, "Temperature"));
		push (@P, $P_std->Cell($row, "Pressure"));
	}
	
	$T_std->Delete;
	$T_analysis->TemperatureChart->Delete;
	$P_std->Delete;
	$P_analysis->PressureChart->Delete;

	# Use calculateStatistics to calculate stats for the properties
	my ($Tavg, $Tsd) = calculateStatistics(@T);
	my ($Pavg, $Psd) = calculateStatistics(@P);
	
	$textDoc->Append("\n                 Average      StdDev\n");
	$textDoc->Append(sprintf "Temperature  %11.5g %11.5g\n", $Tavg, $Tsd);
	$textDoc->Append(sprintf "Pressure     %11.5g %11.5g\n", $Pavg, $Psd);

	# write these to study table
	if ($row_counter == 0)
	{
		my $sheet = $statTable->InsertSheet($nstatsheets,"Thermo");
		$nstatsheets++;
		$statTable->ColumnHeading(0) = "Reaction Radius (A)";
		$statTable->ColumnHeading(1) = "Average Temp (K)";
		$statTable->ColumnHeading(2) = "Std Dev";
		$statTable->ColumnHeading(3) = "Average Pressure (GPa)";
		$statTable->ColumnHeading(4) = "Std Dev";
	}
	my $sheet = $statTable->Sheets("Thermo");
	$sheet->InsertRow;
	$sheet->Cell($row_counter,0) = $distance;
	$sheet->Cell($row_counter,1) = $Tavg;
	$sheet->Cell($row_counter,2) = $Tsd;
	$sheet->Cell($row_counter,3) = $Pavg;
	$sheet->Cell($row_counter,4) = $Psd;
}

##########################################################################################################

# Calculate the mean and standard deviation

sub calculateStatistics 
{
	my @property = @_;
	
	my $numberValues = @property;
	
	# calculate Mean
	my $mean = 0;
	foreach my $value (@property) {
		$mean += $value;
	}
	$mean /= $numberValues;
	
	# Calculate standard deviation
	my $stdDev = 0;
	foreach my $value (@property) {
		my $diffsq = ($value - $mean)**2;
		$stdDev += $diffsq;	
	}
	$stdDev = sqrt($stdDev/($numberValues - 1));
	
	return $mean, $stdDev;
}

#########################################################################################################

# Recalculate charge groups

sub DivideAndConquer
{
	my ($doc, $Forcite) = @_;
	
	# Single point energy to generate new charge groups
	$Forcite->Energy->Run($doc, [
		AssignForcefieldTypes			=> "Yes",
		ChargeAssignment			=> "Forcefield assigned",
		AssignChargeGroups			=> "Yes",
		ChargeGroupAssignmentMethod             => "Divide-and-conquer", 
		"3DPeriodicElectrostaticSummationMethod"=> "Group based",
		WriteLevel				=> "Silent"
	]);
	
	# Check max charge group size
	my $max1 = 0;
	my $max2 = 0;
	my $max3 = 0;
	foreach my $cg (@{$doc->UnitCell->ChargeGroups})
	{
		$max1 = abs($cg->NetCharge) 		if ($max1 < abs($cg->NetCharge));
		$max2 = $cg->ChargeGroupAtoms->Count 	if ($max2 < $cg->ChargeGroupAtoms->Count);
		$max3 = $cg->ChargeGroupSize 		if ($max3 < $cg->ChargeGroupSize);
	}
	$textDoc->Append("  DivideAndConquer charge groups reassigned\n");
	$textDoc->Append(sprintf "    max: %.1g charge, %d atoms, %.1f Angstrom\n", $max1, $max2, $max3);
	
	# Check net charge
	my $qnet = 0;
	foreach (@{$doc->UnitCell->Atoms})
	{
		$qnet += $_->Charge;
	}
	warn "    WARNING: System is not neutral. Net charge = $qnet\n" if (abs($qnet) > 0.2);
	
	return $doc;
}


#########################################################################################################

# Create a set containing crosslinked atoms and bonds

sub XlinkSet
{
	my $doc = shift;

	my @xlinked_atoms;
	foreach my $bond (@{$doc->UnitCell->Bonds}) 
	{
		if ($bond->Name =~ /^xlink/) 
		{
			push @xlinked_atoms, $bond->Atom1;
			push @xlinked_atoms, $bond->Atom2;
			push @xlinked_atoms, $bond;
		}
	}
	return if ( scalar(@xlinked_atoms) == 0 );

	$textDoc->Append( "\nCreating crosslink set\n");
	my $set = $doc->CreateSet("Crosslinks", \@xlinked_atoms);
	$set->IsVisible = 0;
}

#########################################################################################################

# Geometry optimize with current Forcite settings and given number of steps, ignoring fatal errors
# Requires $Forcite, $textDoc

sub ForciteGeomOpt
{
	my $t0 = time;
	my $doc1 = shift;
	my $steps = shift;
	
	my $results;	
	eval 
	{
		$results = $Forcite->GeometryOptimization->Run($doc1, 
		Settings(
	                   MaxIterations => $steps,
	                   OptimizeCell => "No", 
	                   MaxForce => 0.001, 
	                   MaxStress => 0.001, 
	                   MaxDisplacement => 1e-005, 
	                   MaxEnergy => 2e-005, 
	                   UseMaxStress => "Yes", 
	                   UseMaxDisplacement => "Yes"));
	};

	if ($@) 
	{	 
	 	$textDoc->Append( "ForciteGeomOpt: Failed during geometry optimization\n");
	 	$textDoc->Append( $@);
	}

	if (DEBUG) { 
		$textDoc->Append(sprintf "ForciteGeomOpt %d steps, %d seconds\n", $steps, time-$t0); 
		$textDoc->Save; 
	}

	return $results;
}

#########################################################################################################

# Forcite dynamics
# Required globals: $Forcite, $textDoc
# Usage: $results = ForciteDynamics($doc, $steps, $ensemble, (optionalSetting1 => 100, ...))

sub ForciteDynamics
{
	# Start the timer
	my $t0 = time;
	
	# Required arguments
	my $doc1 = shift;
	my $steps = shift;
	my $ensemble = shift;
	
	# Formulate the settings as a perl array
	my @settings = (
		NumberOfSteps	=> $steps,
		Ensemble3D	=> $ensemble,
	);
	
	# The remainder are assumed to be custom settings
	push @settings, @_;
			
	# Run the dynamics inside an eval to prevent failed runs from stopping script
	my $results;
	eval 
	{
		$results = $Forcite->Dynamics->Run($doc1, \@settings);
	};
	if ($@) 
	{
		$textDoc->Append( "ERROR: ForciteDynamics failed\n");
		$textDoc->Append( $@);
		die "Failed in ForciteDynamics\n";
	}

	# Report time used
	if (DEBUG) 
	{ 
		$textDoc->Append(sprintf "ForciteDynamics %d steps, %s ensemble, %d seconds\n", 
			$steps, $ensemble, time-$t0);
		$textDoc->Save;
	}

	return $results;	
}

