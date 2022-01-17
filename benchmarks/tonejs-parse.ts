import * as fs from 'fs'
import glob from 'glob'
import { Midi } from '@tonejs/midi'

const n = Number(process.argv.at(3))
if (isNaN(n)) throw new Error()
let files = glob.sync('data/**/*.mid')
const times = []
for (let i = 0; i < n; i++) {
    const st = new Date().getTime()
    try {
        const file = fs.readFileSync(files[Math.round(Math.random()*files.length)])
        new Midi(file)
    } catch { }
    times.push((new Date()).getTime() - st)
}

console.log(`[tonejs] mean read+parse time (n=${n}): ${times.reduce((acc, n) => acc+n)/times.length}`)