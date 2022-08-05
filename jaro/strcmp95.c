// Original version of code found here:
// http://web.archive.org/web/20100227020019/http://www.census.gov/geo/msb/stand/strcmp.c
// (Should be saved here as strcmp95.orig.c)

// The code has been modified so that
// - it can be called and passed args from command line
// - it now prints out several values from the function, so the output of this
//   function can be compared to the output of a python one.

// Use as follows (assuming it's compiled as strcmp95)
// ./strcmp95 string1 string2 flag_str
// where flag_str is a 2-char string, containing only the chars '1' and '0',
// which set up the values of the ind_c array (see below)

/* strcmp95.c   Version 2						      */

/* The strcmp95 function returns a double precision value from 0.0 (total
   disagreement) to 1.0 (character-by-character agreement).  The returned
   value is a measure of the similarity of the two strings.                   */

/* Date of Release:  Jan. 26, 1994					      */
/* Modified: April 24, 1994  Corrected the processing of the single length
             character strings.
   Authors:  This function was written using the logic from code written by
             Bill Winkler, George McLaughlin and Matt Jaro with modifications
             by Maureen Lynch.
   Comment:  This is the official string comparator to be used for matching
             during the 1995 Test Census.                                     */

#include <ctype.h>
#include <string.h>
#include <stdio.h>

#define NOTNUM(c)	((c>57) || (c<48))
#define INRANGE(c)      ((c>0)  && (c<91))
#define MAX_VAR_SIZE 61
#define NULL60 "                                                            "

double  strcmp95(char *ying, char *yang, long y_length, int ind_c[])

{
/* Arguments:

   ying and yang are pointers to the 2 strings to be compared.  The strings
   need not be NUL-terminated strings because the length is passed.

   y_length is the length of the strings.

   ind_c is an array that is used to define whether certain options should be
   activated.  A nonzero value indicates the option is deactivated.
   The options are:
     ind_c[0] Increase the probability of a match when the number of matched
              characters is large.  This option allows for a little more
              tolerance when the strings are large.  It is not an appropriate
              test when comparing fixed length fields such as phone and
              social security numbers.
     ind_c[1] All lower case characters are converted to upper case prior
              to the comparison.  Disabling this feature means that the lower
              case string "code" will not be recognized as the same as the
              upper case string "CODE".  Also, the adjustment for similar
              characters section only applies to uppercase characters.

   The suggested values are all zeros for character strings such as names.    */

static	int	pass=0,	adjwt[91][91];
static	char	sp[39][2] =
 {'A','E',  'A','I',  'A','O',  'A','U',  'B','V',  'E','I',  'E','O',  'E','U',
  'I','O',  'I','U',  'O','U',  'I','Y',  'E','Y',  'C','G',  'E','F',
  'W','U',  'W','V',  'X','K',  'S','Z',  'X','S',  'Q','C',  'U','V',
  'M','N',  'L','I',  'Q','O',  'P','R',  'I','J',  '2','Z',  '5','S',
  '8','B',  '1','I',  '1','L',  '0','O',  '0','Q',  'C','K',  'G','J',
  'E',' ',  'Y',' ',  'S',' '};

char    ying_hold[MAX_VAR_SIZE],
        yang_hold[MAX_VAR_SIZE],
        ying_flag[MAX_VAR_SIZE],
        yang_flag[MAX_VAR_SIZE];

double  weight,	Num_sim;

long    minv,   search_range,   lowlim,    ying_length,
        hilim,  N_trans,        Num_com,   yang_length;

int	yl1,	yi_st,	N_simi;

register        int     i,      j,      k;

/* Initialize the adjwt array on the first call to the function only.
   The adjwt array is used to give partial credit for characters that
   may be errors due to known phonetic or character recognition errors.
   A typical example is to match the letter "O" with the number "0"           */
if (!pass) {
  pass++;
  for (i=0; i<91; i++) for (j=0; j<91; j++) adjwt[i][j] = 0;
  for (i=0; i<36; i++) {
        char i0 = sp[i][0];
        char i1 = sp[i][1];
        // printf("indices sp[%d][0]=%c, sp[%d][1]=%c\n", i, i0, i, i1);
        // printf("  adjwt[%d][%d]=3, adjwt[%d][%d]=3\n", i0, i1, i1, i0);
    adjwt[sp[i][0]][sp[i][1]] = 3;
    adjwt[sp[i][1]][sp[i][0]] = 3;
} }

/* If either string is blank - return - added in Version 2                    */
if (!strncmp(ying,NULL60,y_length)) return(0.0);
if (!strncmp(yang,NULL60,y_length)) return(0.0);

/* Identify the strings to be compared by stripping off all leading and
   trailing spaces.							      */
k = y_length - 1;
for(j = 0;((ying[j]==' ') && (j < k));j++);
for(i = k;((ying[i]==' ') && (i > 0));i--);
ying_length = i + 1 - j;
yi_st = j;
printf("\n");
printf("ying start: %d\n", yi_st);
printf("ying length: %ld\n", ying_length);

for(j = 0;((yang[j]==' ') && (j < k));j++);
for(i = k;((yang[i]==' ') && (i > 0));i--);
yang_length = i + 1 - j;
printf("yang start: %d\n", j);
printf("yang length: %ld\n", yang_length);

ying_hold[0]=yang_hold[0]=0;
strncat(ying_hold,&ying[yi_st],ying_length);
strncat(yang_hold,&yang[j],yang_length);

if (ying_length > yang_length) {
  search_range = ying_length;
  minv = yang_length;
  }
 else {
  search_range = yang_length;
  minv = ying_length;
  }

/* If either string is blank - return                                         */
/* if (!minv) return(0.0);                   removed in version 2             */

/* Blank out the flags							      */
ying_flag[0] = yang_flag[0] = 0;
strncat(ying_flag,NULL60,search_range);
strncat(yang_flag,NULL60,search_range);
search_range = (search_range/2) - 1;
if (search_range < 0) search_range = 0;   /* added in version 2               */

/* Convert all lower case characters to upper case.                           */
if (!ind_c[1]) {
  for (i = 0;i < ying_length;i++) if (islower(ying_hold[i])) ying_hold[i] -= 32;
  for (j = 0;j < yang_length;j++) if (islower(yang_hold[j])) yang_hold[j] -= 32;
}
printf("Search range: %ld\n", search_range);
printf("Minv: %ld\n", minv);
printf("ying hold: '%s'\n", ying_hold);
printf("yang hold: '%s'\n", yang_hold);
printf("\n");

/* Looking only within the search range, count and flag the matched pairs.    */
Num_com = 0;
yl1 = yang_length - 1;
for (i = 0;i < ying_length;i++) {
  lowlim = (i >= search_range) ? i - search_range : 0;
  hilim = ((i + search_range) <= yl1) ? (i + search_range) : yl1;
  printf("%d. Looking for char %c in range [%ld, %ld (incl)]\n", i, ying_hold[i],lowlim, hilim);
  for (j = lowlim;j <= hilim;j++)  {
    printf("   j:%2d   char: %c\n", j, yang_hold[j]);
    if ((yang_flag[j] != '1') && (yang_hold[j] == ying_hold[i])) {
        yang_flag[j] = '1';
        ying_flag[i] = '1';
        Num_com++;
        break;
} } }
printf("Num com: %ld\n", Num_com);
printf("ying flag: '%s'\n", ying_flag);
printf("yang flag: '%s'\n", yang_flag);

/* If no characters in common - return                                        */
if (!Num_com) return(0.0);

/* Count the number of transpositions                                         */
k = N_trans = 0;
for (i = 0;i < ying_length;i++) {
  if (ying_flag[i] == '1') {
    for (j = k;j < yang_length;j++) {
        if (yang_flag[j] == '1') {
         k = j + 1;
         break;
    } }
    if (ying_hold[i] != yang_hold[j]) N_trans++;
} }
printf("Transpositions: %ld\n", N_trans);
N_trans = N_trans / 2;

weight= Num_com / ((double) ying_length) + Num_com / ((double) yang_length)
   + ((double) (Num_com - N_trans)) / ((double) Num_com);
weight = weight / 3.0;
printf("First weight: %.6f\n", weight);

/* adjust for similarities in nonmatched characters                           */
N_simi = 0;
if (minv > Num_com) {
  for (i = 0;i < ying_length;i++) {
    if (ying_flag[i] == ' ' && INRANGE(ying_hold[i])) {
      for (j = 0;j < yang_length;j++) {
        if (yang_flag[j] == ' ' && INRANGE(yang_hold[j])) {
          if (adjwt[ying_hold[i]][yang_hold[j]] > 0) {
            N_simi += adjwt[ying_hold[i]][yang_hold[j]];
            yang_flag[j] = '2';
            break;
} } } } } }
Num_sim = ((double) N_simi)/10.0 + Num_com;
printf("N_simi : %d\n", N_simi);
printf("Num sim: %.6f\n", Num_sim);
printf("ying flag: '%s'\n", ying_flag);
printf("yang flag: '%s'\n", yang_flag);

/* Main weight computation.						      */
weight= Num_sim / ((double) ying_length) + Num_sim / ((double) yang_length)
   + ((double) (Num_com - N_trans)) / ((double) Num_com);
weight = weight / 3.0;
printf("Weight: %.6f\n", weight);
/* Continue to boost the weight if the strings are similar                    */
if (weight > 0.7) {

  /* Adjust for having up to the first 4 characters in common                 */
  j = (minv >= 4) ? 4 : minv;
  for (i=0;((i<j)&&(ying_hold[i]==yang_hold[i])&&(NOTNUM(ying_hold[i])));i++)
    printf("pre-match: %d\n", i);
  if (i) {
    printf("final pre-match: %d\n", i);
    weight += i * 0.1 * (1.0 - weight);
  }
  printf("Adjusted weight: %.6f\n", weight);

  /* Optionally adjust for long strings.                                      */
  /* After agreeing beginning chars, at least two more must agree and
       the agreeing characters must be > .5 of remaining characters.          */
  if ((!ind_c[0]) && (minv>4) && (Num_com>i+1) && (2*Num_com>=minv+i))
  if (NOTNUM(ying_hold[0])) {
    weight += (double) (1.0-weight) *
          ((double) (Num_com-i-1) / ((double) (ying_length+yang_length-i*2+2)));
    printf("Re-adjusted weight: %.6f\n", weight);
  }
 }

return(weight);

} /* strcmp95 */

int main(int argc, char* argv[]) {

    long ying_length, yang_length, length, diff;
    char* ying;
    char* yang;
    char ying_hold[MAX_VAR_SIZE], yang_hold[MAX_VAR_SIZE];
    register int i, j, k;
    double weight;

    int flags[2];
    char *flag_str;

    /*for (i=0; i<argc; i++) {
        printf("Arg %d: '%s'\n", i, argv[i]);
    } */

    flag_str = argv[3];
    // printf("flag_str: '%s'\n", flag_str);
    for (i=0; i<2; i++) {
        flags[i] = 1 ? flag_str[i] == 49 : 0;
        // printf("flag bit %d: '%d'\n", i, flag_str[i]);
        // printf("flag bit %d: '%d'\n", i, flags[i]);
    }
    // flags[0] = 0;
    // flags[1] = 1;

    ying = argv[1];
    yang = argv[2];
    ying_length = strlen(ying);
    yang_length = strlen(yang);
    length = (ying_length > yang_length) ? ying_length : yang_length;

    printf("ying: '%s' (len %ld)\n", ying, ying_length);
    printf("yang: '%s' (len %ld)\n", yang, yang_length);
    printf("length: %ld\n", length);
    printf("flags: %d %d\n", flags[0], flags[1]);

    ying_hold[0] = yang_hold[0] = 0;
    // strncat(ying_hold,DOT60,length);
    // strncat(yang_hold,DOT60,length);
    strncat(ying_hold,NULL60,length);
    strncat(yang_hold,NULL60,length);

    // printf("ying_hold: '%s'\n", ying_hold);
    // printf("yang_hold: '%s'\n", yang_hold);
    for (i=0; i<ying_length; i++)
        ying_hold[i] = ying[i];
    for (i=0; i<yang_length; i++)
        yang_hold[i] = yang[i];
    // printf("ying_hold: '%s'\n", ying_hold);
    // printf("yang_hold: '%s'\n", yang_hold);

    strcmp95(ying_hold, yang_hold, length, flags);
}
