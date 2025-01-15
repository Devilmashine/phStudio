/**
 * Groups consecutive time slots together
 * @param times Array of time strings in HH:mm format
 * @returns Array of grouped consecutive time slots
 */
export const groupConsecutiveSlots = (times: string[]): string[][] => {
  if (!times.length) return [];

  const sortedTimes = [...times].sort((a, b) => {
    const hourA = parseInt(a.split(':')[0]);
    const hourB = parseInt(b.split(':')[0]);
    return hourA - hourB;
  });

  const timeGroups: string[][] = [];
  let currentGroup: string[] = [sortedTimes[0]];
  
  for (let i = 1; i < sortedTimes.length; i++) {
    const currentHour = parseInt(sortedTimes[i].split(':')[0]);
    const prevHour = parseInt(currentGroup[currentGroup.length - 1].split(':')[0]);
    
    if (currentHour === prevHour + 1) {
      currentGroup.push(sortedTimes[i]);
    } else {
      timeGroups.push([...currentGroup]);
      currentGroup = [sortedTimes[i]];
    }
  }
  
  if (currentGroup.length) {
    timeGroups.push([...currentGroup]);
  }
  
  return timeGroups;
};