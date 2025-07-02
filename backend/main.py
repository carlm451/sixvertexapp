import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SixVertexModel:
    def __init__(self, Lx, Ly, n):
        self.Lx = Lx
        self.Ly = Ly
        self.n = n
        self.vertical_spins = np.ones((Ly + 1, Lx))
        self.horizontal_spins = np.zeros((Ly, Lx))

    def generate_configuration(self):
        down_spins = np.zeros((self.Ly + 1, self.n), dtype=int)
        range_lx = np.arange(1, self.Lx + 1)
        down_spins[0] = np.sort(np.random.choice(range_lx, self.n, replace=False))

        for i in range(1, self.Ly + 1):
            x_list = down_spins[i - 1]
            test = False
            count = 0
            while not test and count < 1000:
                y_list = np.sort(np.random.choice(range_lx, self.n, replace=False))
                
                x_list2 = np.append(x_list[1:], self.Lx)
                x_list3 = np.insert(x_list[:-1], 0, 1)

                test1 = np.all(x_list <= y_list) and np.all(y_list <= x_list2)
                test2 = np.all(x_list3 <= y_list) and np.all(y_list <= x_list)

                test = test1 or test2
                count += 1
            down_spins[i] = y_list

        for i in range(self.Ly + 1):
            for pos in down_spins[i]:
                self.vertical_spins[i, pos - 1] = -1

        for i in range(self.Ly):
            lower_row = self.vertical_spins[i]
            upper_row = self.vertical_spins[i + 1]
            row = np.zeros(self.Lx)

            if np.array_equal(lower_row, upper_row):
                row.fill(np.random.choice([-1, 1]))
            else:
                for j in range(self.Lx):
                    if lower_row[j] == 1 and upper_row[j] == -1:
                        row[j] = -1
                        row[(j + 1) % self.Lx] = 1
                    elif lower_row[j] == -1 and upper_row[j] == 1:
                        row[j] = 1
                        row[(j + 1) % self.Lx] = -1
                
                for j in range(self.Lx):
                    if row[j] == 0:
                        count = 1
                        left_index = (j - count + self.Lx) % self.Lx
                        while row[left_index] == 0 and count < self.Lx:
                            count += 1
                            left_index = (j - count + self.Lx) % self.Lx
                        row[j] = row[left_index]

            self.horizontal_spins[i] = row
        
        self.vertical_spins = self.vertical_spins[:-1, :].tolist()
        self.horizontal_spins = self.horizontal_spins.tolist()


class GridSize(BaseModel):
    Lx: int
    Ly: int
    n: int | None = None

@app.post("/generate")
def generate(grid_size: GridSize):
    n = grid_size.n if grid_size.n is not None else grid_size.Lx // 2
    model = SixVertexModel(grid_size.Lx, grid_size.Ly, n)
    model.generate_configuration()
    return {"verticalSpins": model.vertical_spins, "horizontalSpins": model.horizontal_spins}