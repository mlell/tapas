
mkdir run
mkdir log

: ${d_fastq:?"d_fastq must be defined! (directory of FASTQ input)"}

export s_map_bwa="$pr/mapper-compare/bwa/map-reads-bwa.sh"
export bwa_index="$pr/mapper-compare/bwa/Usp_mito/Usp_mito"

