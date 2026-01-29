class Slab:
    def __init__(self, object_size, objects_per_slab):
        self.object_size = object_size
        self.count = objects_per_slab
        # Symulacja ciągłego bloku pamięci
        self.memory = [bytearray(object_size) for _ in range(objects_per_slab)]
        self.bitmap = [False] * objects_per_slab

    def allocate(self):
        for i in range(self.count):
            if not self.bitmap[i]:
                self.bitmap[i] = True
                return i
        return None

    def deallocate(self, index):
        if 0 <= index < self.count:
            self.bitmap[index] = False

    def is_full(self):
        return all(self.bitmap)

    def contains(self, slab_ref):
        return self == slab_ref


class SlabCache:
    def __init__(self, object_size, objects_per_slab):
        self.object_size = object_size
        self.objects_per_slab = objects_per_slab
        self.slabs = []

    def alloc(self):
        for slab in self.slabs:
            idx = slab.allocate()
            if idx is not None:
                return (slab, idx)

        # Tworzenie nowego slaba, gdy brak miejsca
        new_slab = Slab(self.object_size, self.objects_per_slab)
        self.slabs.append(new_slab)
        idx = new_slab.allocate()
        return (new_slab, idx)

    def free(self, ptr):
        slab_ref, idx = ptr
        for slab in self.slabs:
            if slab.contains(slab_ref):
                slab.deallocate(idx)
                return
        raise ValueError("Pointer not found in any slab")

    def debug_state(self):
        for i, slab in enumerate(self.slabs):
            print(f"Slab {i}: {['[X]' if b else '[ ]' for b in slab.bitmap]}")


# --- PRZYKŁAD DZIAŁANIA ---

cache = SlabCache(object_size=32, objects_per_slab=2)

print("1. Alokacja dwóch obiektów (Slab 0 się zapełnia):")
p1 = cache.alloc()
p2 = cache.alloc()
cache.debug_state()

print("\n2. Alokacja trzeciego obiektu (Tworzony jest Slab 1):")
p3 = cache.alloc()
cache.debug_state()

print("\n3. Zwolnienie drugiego obiektu (Zwolnienie miejsca w Slab 0):")
cache.free(p2)
cache.debug_state()

print("\n4. Ponowna alokacja (Zajęcie wolnego miejsca w Slab 0 przed użyciem Slab 1):")
p4 = cache.alloc()
cache.debug_state()
