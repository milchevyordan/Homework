import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';


export interface Repo {
    name: string;
    language: string | null;
    url: string;
    description: string | null;
    stars: number;
    fork: boolean;
}

export interface Language {
    name: string;
    count: number;
}

export interface GithubUserResponse {
    username: string;
    name: string | null;
    avatar_url: string | null;
    profile_url: string | null;
    followers: number;
    repos: Repo[];
    repo_count: number;
    most_used_language: string | null;
    languages: Language[];
    messages: { followers?: string; repos?: string; languages?: string };
}


@Injectable({
    providedIn: 'root'
})

export class GithubService {

    private apiUrl = 'http://127.0.0.1:8000/api/user';

    constructor(private http: HttpClient) {}

    getUser(username: string): Observable<GithubUserResponse> {
        const params = new HttpParams().set('username', username);
        return this.http.get<GithubUserResponse>(this.apiUrl, { params });
    }

}
