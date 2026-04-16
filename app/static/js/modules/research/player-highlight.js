export function resolveActiveTimedItem(items, currentMs) {
  if (!Array.isArray(items) || !items.length) {
    return { itemId: null, itemIndex: -1 };
  }

  let previousItem = null;
  for (let index = 0; index < items.length; index += 1) {
    const item = items[index];
    const normalizedItem = {
      itemId: item.itemId,
      itemIndex: Number.isInteger(item.itemIndex) ? item.itemIndex : index,
    };

    if (currentMs >= item.startMs && currentMs <= item.endMs) {
      return normalizedItem;
    }

    if (currentMs < item.startMs) {
      return previousItem || { itemId: null, itemIndex: -1 };
    }

    previousItem = normalizedItem;
  }

  return previousItem || { itemId: null, itemIndex: -1 };
}