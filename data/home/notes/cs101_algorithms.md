# CS101 Algorithms - Lecture Notes

## Big-O notation
Big-O describes how runtime grows with input size n. Drop constants and lower-order terms.
Common classes: O(1), O(log n), O(n), O(n log n), O(n^2).

## Sorting algorithms
Merge sort splits the list, sorts halves recursively, and merges: O(n log n) time, O(n) extra space.
Quicksort picks a pivot and partitions: O(n log n) average, O(n^2) worst case.
Insertion sort is O(n^2) but fast on nearly sorted data.

## Recursion
A recursive function needs a base case and a step that moves toward it.
The call stack stores each pending call; deep recursion can overflow the stack.

## Dynamic programming
DP solves overlapping subproblems once and stores results (memoization or a bottom-up table).
Classic examples: Fibonacci, knapsack, longest common subsequence.
